import abc
import dataclasses as dcs
import functools
import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Optional

from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from ..helper import DataclsCfg
from ..utils import to_json
from .chains import Chains
from .infomap import append, query


@dataclass
class BaseTask:
    task: str = ""
    seq_name: str = ""

    parent: Optional["BaseTask"] = dcs.field(
        default=None, repr=False, metadata=DataclsCfg(no_meta=True, no_hash=True).D
    )
    children: list["BaseTask"] = dcs.field(
        default_factory=list, init=False, repr=False, metadata=DataclsCfg(no_meta=True, no_hash=True).D
    )
    chains: Chains = dcs.field(default_factory=Chains, repr=False)

    def __post_init__(self) -> None:
        if (parent := self.parent) is not None:
            # Generate `self.chains` following `parent`
            chains = parent.chains.copy()
            chains.objs.append(parent)
            self.chains = chains
            # Appending reverse hooks to `parent`
            parent.children.append(self)
            # Infer `seq_name` from `parent`
            if not self.seq_name:
                self.seq_name = parent.seq_name

    @classmethod
    def unmarshal(cls, dic: dict):
        kwargs = {}

        for field in dcs.fields(cls):
            if not field.init:
                continue
            if not (val := dic.get(field.name, None)):
                continue
            if hasattr(field.type, 'unmarshal'):
                val = field.type.unmarshal(val)
            kwargs[field.name] = val

        return cls(**kwargs)

    def marshal(self, exclude_if: Callable[[dcs.Field], bool]) -> dict:
        dic = {}

        for field in dcs.fields(self):
            if exclude_if(field):
                continue

            val = getattr(self, field.name)

            if hasattr(val, "marshal"):
                dic[field.name] = val.marshal()
            else:
                dic[field.name] = val

        return dic

    @functools.cached_property
    def metainfo(self) -> str:
        marshaled = self.marshal(exclude_if=lambda f: DataclsCfg.from_meta(f.metadata).no_meta)
        metainfo = to_json(marshaled, pretty=True)
        return metainfo

    @functools.cached_property
    def hash(self) -> str:
        marshaled = self.marshal(exclude_if=lambda f: DataclsCfg.from_meta(f.metadata).no_hash)
        hashbytes = to_json(marshaled).encode('utf-8')
        hash_ = hashlib.sha1(hashbytes, usedforsecurity=False)
        return hash_.hexdigest()

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

    def dump_metainfo(self) -> None:
        with (self.dstdir / "metainfo.json").open('w', encoding='utf-8') as f:
            f.write(self.metainfo)

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
            self.dump_metainfo()
            append(self, self.dstdir)
