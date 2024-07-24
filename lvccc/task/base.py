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
from ..utils import to_json
from .chain import Chain
from .infomap import append, query

TSelfTask = TypeVar("TSelfTask", bound="BaseTask")
TDerivedTask = TypeVar("TDerivedTask", bound="BaseTask")


@dataclass
class BaseTask(Generic[TSelfTask]):
    task: str = ""
    seq_name: str = ""

    children: list[TDerivedTask] = dcs.field(default_factory=list, init=False, repr=False)
    chain: Chain = dcs.field(default_factory=Chain, init=False, repr=False)

    @functools.cached_property
    def parent(self) -> TDerivedTask | None:
        if len(self.chain) > 0:
            return self.chain[-1]
        else:
            return None

    def with_parent(self: TSelfTask, parent: TDerivedTask) -> TSelfTask:
        # Appending `parent.params` to chain
        chain = parent.chain.copy()
        chain.objs.append(parent.fields)
        self.chain = chain
        # Appending reverse hooks to `parent`
        parent.children.append(self)

        # Infer `seq_name` from `parent`
        if not self.seq_name:
            self.seq_name = parent.seq_name
        if not self.frames:
            self.frames = parent.frames

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
        hashbytes = to_json(self.chain_with_self.objs).encode('utf-8')
        hashint = xxhash.xxh3_64_intdigest(hashbytes)
        return hashint

    @property
    def shorthash(self) -> str:
        return hex(self.hash)[2:6]

    @abc.abstractmethod
    @functools.cached_property
    def dirname(self) -> str: ...

    @functools.cached_property
    def dstdir(self) -> Path:
        config = get_config()

        if self.parent is not None and self.parent.dirname:
            parent_dirname = f"-{self.parent.dirname}"
        else:
            parent_dirname = ""
        self_dirname = f"-{self.dirname}" if self.dirname else ""
        real_dirname = f"{self.task}{parent_dirname}{self_dirname}-{self.shorthash}"

        return config.path.output / "tasks" / real_dirname

    def _dump_taskinfo(self) -> None:
        with (self.dstdir / "task.json").open('w', encoding='utf-8') as f:
            taskinfo = self.chain_with_self.serialized_str
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
            self._dump_taskinfo()
            append(self, self.dstdir)
            log = get_logger()
            log.info(f"Task `{self.dstdir.name}` completed!")
