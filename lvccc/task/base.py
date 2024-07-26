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
from ..helper import to_json
from ..logging import get_logger
from .abc import TRetTask, TSelfTask, TVarTask
from .chain import Chain
from .infomap import append, query

TTask = TypeVar("TTask", bound="BaseTask")


@dataclass
class BaseTask(Generic[TSelfTask]):
    task: str = ""

    children: list[TTask] = dcs.field(default_factory=list, init=False, repr=False)
    chain: Chain = dcs.field(default_factory=Chain, init=False, repr=False)

    @functools.cached_property
    def parent(self) -> TRetTask | None:
        if len(self.chain) > 0:
            return self.chain[-1]
        else:
            return None

    def with_parent(self: TSelfTask, parent: TVarTask) -> TSelfTask:
        # Appending `parent.params` to chain
        chain = parent.chain.copy()
        chain.objs.append(parent.fields)
        self.chain = chain

        # Appending reverse hooks to `parent`
        parent.children.append(self)

        return self

    @classmethod
    def deserialize(cls, fields: dict) -> TSelfTask:
        kwargs = {}

        for field in dcs.fields(cls):
            if not field.init:
                continue
            if not (val := fields.get(field.name, None)):
                continue
            kwargs[field.name] = val

        return cls(**kwargs)

    def serialize(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict:
        dic = {}

        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            dic[field.name] = val

        return dic

    @functools.cached_property
    def fields(self) -> dict:
        fields = self.serialize()
        return fields

    @functools.cached_property
    def chain_with_self(self) -> Chain:
        objs = self.chain.objs.copy()
        objs.append(self.fields)
        chain = Chain(objs)
        return chain

    @functools.cached_property
    def hash(self) -> int:
        hashbytes = self.chain_with_self.to_json().encode('utf-8')
        hashint = xxhash.xxh3_64_intdigest(hashbytes)
        return hashint

    @property
    def shorthash(self) -> str:
        return hex(self.hash)[2:6]

    @abc.abstractmethod
    @functools.cached_property
    def tag(self) -> str: ...

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


class NonRootTask(Generic[TSelfTask], BaseTask[TSelfTask]):
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
