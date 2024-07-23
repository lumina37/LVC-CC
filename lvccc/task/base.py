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
        chains = parent.chain.copy()
        chains.objs.append(parent.__params)
        self.chain = chains
        # Appending reverse hooks to `parent`
        parent.children.append(self)

        # Infer `seq_name` from `parent`
        if not self.seq_name:
            self.seq_name = parent.seq_name
        if not self.frames:
            self.frames = parent.frames

        return self

    @classmethod
    def unmarshal(cls, dic: dict):
        kwargs = {}

        for field in dcs.fields(cls):
            if not field.init:
                continue
            if not (val := dic.get(field.name, None)):
                continue
            kwargs[field.name] = val

        return cls(**kwargs)

    def marshal(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict:
        dic = {}

        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            dic[field.name] = val

        return dic

    @functools.cached_property
    def __params(self) -> dict:
        params = self.marshal()
        return params

    @functools.cached_property
    def __taskinfo(self) -> list[dict]:
        taskinfo = self.chain.objs.copy()
        taskinfo.append(self.__params)
        return taskinfo

    @functools.cached_property
    def taskinfo_str(self) -> str:
        return to_json(self.__taskinfo, pretty=True)

    @functools.cached_property
    def hash(self) -> str:
        hashbytes = to_json(self.__taskinfo).encode('utf-8')
        hashhex = xxhash.xxh3_64_hexdigest(hashbytes)
        return hashhex

    @property
    def shorthash(self) -> str:
        return self.hash[:4]

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

    def __dump_taskinfo(self) -> None:
        with (self.dstdir / "task.json").open('w', encoding='utf-8') as f:
            f.write(self.taskinfo_str)

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
            self.__dump_taskinfo()
            append(self, self.dstdir)
            log = get_logger()
            log.info(f"Task `{self.dirname}` completed!")
