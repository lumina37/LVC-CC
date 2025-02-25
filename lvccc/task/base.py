from __future__ import annotations

import abc
import dataclasses as dcs
import functools
import time
import traceback
import zlib
from typing import TYPE_CHECKING, ClassVar

from ..config import get_config
from ..helper import mkdir, to_json
from ..logging import get_logger
from .chain import Chain
from .infomap import append, query

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from .abc import ProtoTask


@dcs.dataclass
class BaseTask[TSelfTask]:
    task: ClassVar[str] = ""

    children: list[ProtoTask] = dcs.field(default_factory=list, init=False, repr=False)
    chain: Chain = dcs.field(default_factory=Chain, init=False, repr=False)

    @property
    def parent(self) -> None:
        return None

    def fields(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict:
        fields = {"task": self.task}
        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            fields[field.name] = val
        return fields

    def to_dicts(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> list[dict]:
        fields = self.fields(exclude_if)
        objs = self.chain.objs.copy()
        objs.append(fields)
        return objs

    @classmethod
    def from_dicts(cls, objs: list[dict]) -> TSelfTask:
        fields = objs[-1]

        kwargs = {}
        for field in dcs.fields(cls):
            if not field.init:
                continue
            if (val := fields.get(field.name, None)) is None:
                continue
            kwargs[field.name] = val

        self = cls(**kwargs)
        self.chain.objs = objs[:-1]

        return self

    def to_json(self, pretty: bool = False) -> str:
        json = to_json(self.to_dicts(), pretty=pretty)
        return json

    @functools.cached_property
    def hash(self) -> int:
        hashbytes = self.to_json().encode("utf-8")
        hashint = zlib.adler32(hashbytes)
        return hashint

    @property
    def shorthash(self) -> str:
        return hex(self.hash)[2:6]

    @property
    def self_tag(self) -> str:
        return ""

    @functools.cached_property
    def tag(self) -> str:
        return self.self_tag

    @functools.cached_property
    def dstdir(self) -> Path:
        config = get_config()
        real_dirname = f"{self.task}-{self.tag}-{self.shorthash}"
        return config.dir.output / "tasks" / real_dirname

    def dump_taskinfo(self, target: Path) -> None:
        with target.open("w", encoding="utf-8") as f:
            taskinfo = self.to_json(pretty=True)
            f.write(taskinfo)

    @abc.abstractmethod
    def _inner_run(self) -> None: ...

    def run(self) -> bool:
        if query(self):
            return True

        log = get_logger()

        try:
            mkdir(self.dstdir)
            start_ns = time.monotonic_ns()
            self._inner_run()
            end_ns = time.monotonic_ns()
        except Exception:
            log.error(f"Task `{self.dstdir.name}` failed! Reason: {traceback.format_exc()}")
            return False
        else:
            self.dump_taskinfo(self.dstdir / "task.json")
            append(self, self.dstdir.absolute())
            elasped_s = (end_ns - start_ns) / 1e9
            log.info(f"Task `{self.dstdir.name}` completed! Elapsed time: {elasped_s:.3f}s")
            return True


class RootTask[TSelfTask](BaseTask[TSelfTask]):
    pass


class NonRootTask[TSelfTask](BaseTask[TSelfTask]):
    @functools.cached_property
    def parent(self) -> ProtoTask:
        return self.chain[-1]

    @functools.cached_property
    def tag(self) -> str:
        parent_part = self.parent.tag
        prefix = "-" if self.self_tag else ""
        self_part = prefix + self.self_tag
        tag = parent_part + self_part
        return tag

    @functools.cached_property
    def seq_name(self) -> str:
        return self.chain[0].seq_name

    @functools.cached_property
    def frames(self) -> int:
        return self.chain[0].frames

    def with_parent(self, parent: ProtoTask) -> TSelfTask:
        # Appending `parent.params` to chain
        chain = parent.chain.copy()
        chain.objs.append(parent.fields())
        self.chain = chain

        # Appending reverse hooks to `parent`
        parent.children.append(self)

        return self
