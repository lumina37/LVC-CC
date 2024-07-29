import abc
import dataclasses as dcs
import functools
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Generic, TypeVar

import xxhash
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..logging import get_logger
from .abc import TRetTask, TSelfTask, TVarTask
from .chain import Chain
from .infomap import append, query

TTask = TypeVar("TTask", bound="RootTask")


@dataclass
class RootTask(Generic[TSelfTask]):
    task: str = ""

    children: list[TTask] = dcs.field(default_factory=list, init=False, repr=False)
    chain: Chain = dcs.field(default_factory=Chain, init=False, repr=False)

    @property
    def parent(self) -> None:
        return None

    def fields(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict:
        fields = {}
        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            fields[field.name] = val
        return fields

    def serialize(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> list[dict]:
        fields = self.fields(exclude_if)
        objs = self.chain.objs.copy()
        objs.append(fields)
        return objs

    @classmethod
    def deserialize(cls, objs: list[dict]) -> TSelfTask:
        fields = objs[-1]

        kwargs = {}
        for field in dcs.fields(cls):
            if not field.init:
                continue
            if not (val := fields.get(field.name, None)):
                continue
            kwargs[field.name] = val

        self = cls(**kwargs)
        self.chain.objs = objs[:-1]

        return self

    @functools.cached_property
    def chain_with_self(self) -> Chain:
        chain = Chain(self.serialize())
        return chain

    @functools.cached_property
    def hash(self) -> int:
        hashbytes = self.chain_with_self.to_json().encode('utf-8')
        hashint = xxhash.xxh3_64_intdigest(hashbytes)
        return hashint

    @property
    def shorthash(self) -> str:
        return hex(self.hash)[2:6]

    @property
    def tag(self) -> str:
        return ""

    @functools.cached_property
    def full_tag(self) -> str:
        return self.tag

    @functools.cached_property
    def dstdir(self) -> Path:
        config = get_config()
        real_dirname = f"{self.task}-{self.full_tag}-{self.shorthash}"
        return config.path.output / "tasks" / real_dirname

    def dump_taskinfo(self, target: Path | None = None) -> None:
        if target is None:
            target = self.dstdir / "task.json"
        with target.open('w', encoding='utf-8') as f:
            taskinfo = self.chain_with_self.to_json(pretty=True)
            f.write(taskinfo)

    @abc.abstractmethod
    def _run(self) -> None: ...

    def run(self) -> None:
        if query(self):
            return

        try:
            self._run()
        except Exception:
            traceback.print_exc()
        else:
            self.dump_taskinfo()
            append(self, self.dstdir)
            log = get_logger()
            log.info(f"Task `{self.dstdir.name}` completed!")


class NonRootTask(Generic[TSelfTask], RootTask[TSelfTask]):
    @functools.cached_property
    def parent(self) -> TRetTask:
        return self.chain[-1]

    @functools.cached_property
    def full_tag(self) -> str:
        parent_part = self.parent.full_tag
        prefix = '-' if self.tag else ''
        self_part = prefix + self.tag
        fulltag = parent_part + self_part
        return fulltag

    @functools.cached_property
    def seq_name(self) -> str:
        return self.chain[0].seq_name

    @functools.cached_property
    def frames(self) -> int:
        return self.chain[0].frames

    def with_parent(self, parent: TVarTask) -> TSelfTask:
        # Appending `parent.params` to chain
        chain = parent.chain.copy()
        chain.objs.append(parent.fields())
        self.chain = chain

        # Appending reverse hooks to `parent`
        parent.children.append(self)

        self._post_with_parent()

        return self

    @abc.abstractmethod
    def _post_with_parent(self) -> None: ...
