import abc
import dataclasses as dcs
import functools
import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Generic, TypeVar

from pydantic.dataclasses import dataclass

from ..config.node import get_node_cfg
from ..helper import DataclsCfg
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

    children_: list[TDerivedTask] = dcs.field(
        default_factory=list, init=False, repr=False, metadata=DataclsCfg(is_chain_param=True).D
    )
    chain_: Chain = dcs.field(default_factory=Chain, init=False, repr=False, metadata=DataclsCfg(is_chain_param=True).D)

    @property
    def has_parent(self) -> bool:
        return len(self.chain_) > 1

    @functools.cached_property
    def parent(self) -> TDerivedTask:
        if self.has_parent:
            return self.chain_[-2]
        else:
            return None

    def with_parent(self: TSelfTask, parent: TDerivedTask) -> TSelfTask:
        # Appending `parent.params`` to chain
        chains = parent.chain_.copy()
        chains.objs.append(parent.params)
        self.chain_ = chains
        # Appending reverse hooks to `parent`
        parent.children_.append(self)

        # Infer `seq_name` from `parent`
        if not self.seq_name:
            self.seq_name = parent.seq_name

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

    def marshal(self, exclude_if: Callable[[dcs.Field], bool]) -> dict:
        dic = {}

        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            dic[field.name] = val

        return dic

    @functools.cached_property
    def taskinfo(self) -> str:
        taskinfo = to_json(self.chain_.objs, pretty=True)
        return taskinfo

    @functools.cached_property
    def hash(self) -> str:
        hashbytes = to_json(self.chain_.objs).encode('utf-8')
        hash_ = hashlib.sha1(hashbytes, usedforsecurity=False)
        return hash_.hexdigest()

    @property
    def params(self) -> dict:
        params = self.chain_.objs[-1]
        return params

    @property
    def shorthash(self) -> str:
        return self.hash[:8]

    @abc.abstractmethod
    @functools.cached_property
    def dirname(self) -> str: ...

    @functools.cached_property
    def dstdir(self) -> Path:
        node_cfg = get_node_cfg()
        return node_cfg.path.dataset / "playground" / self.dirname

    def dump_taskinfo(self) -> None:
        with (self.dstdir / "task.json").open('w', encoding='utf-8') as f:
            f.write(self.taskinfo)

    @abc.abstractmethod
    def _run(self) -> None: ...

    def run(self) -> None:
        if query(self):
            return

        try:
            self._run()
        except Exception:
            pass
        else:
            self.dump_taskinfo()
            append(self, self.dstdir)
            log = get_logger()
            log.info(f"Task `{self.dirname}` completed!")
