import abc
import dataclasses as dcs
import functools
import hashlib
import json
from pathlib import Path
from typing import ClassVar, Optional

from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from .infomap import append


@dataclass
class DataclsCfg:
    KEY: ClassVar[str] = 'mca'

    meta_ex: bool = False
    hash_ex: bool = False
    meta_rootonly: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {self.KEY: dcs.asdict(self)}


@dataclass
class BaseTask:
    task: str = ""
    seq_name: str = dcs.field(default="", metadata=DataclsCfg(meta_rootonly=True).to_dict())

    pretask: Optional["BaseTask"] = dcs.field(
        default=None, hash=False, metadata=DataclsCfg(meta_ex=True, hash_ex=True).to_dict(), kw_only=True
    )
    chains: list[dict] = dcs.field(default_factory=list)

    def __post_init__(self):
        if pretask := self.pretask:
            chains = pretask.chains.copy()
            pretask_dic = pretask.metainfo_dic.copy()
            pretask_dic.pop('chains')
            chains.append(pretask_dic)
            self.chains = chains
        if not self.seq_name:
            if not self.chains:
                raise RuntimeError("We cannot infer `seq_name` from chains. Please enter a `seq_name`")
            self.seq_name = self.chains[0]['seq_name']

    @classmethod
    def from_dict(cls, dic: dict):
        kwargs = {field.name: val for field in dcs.fields(cls) if field.init and (val := dic.get(field.name, None))}
        return cls(**kwargs)

    @functools.cached_property
    def metainfo_dic(self) -> dict:
        dic = {}

        for field in dcs.fields(self):
            metacfg = DataclsCfg(**field.metadata.get(DataclsCfg.KEY, {}))
            if metacfg.meta_ex:
                continue

            val = getattr(self, field.name)
            if hasattr(val, "to_dict"):
                dic[field.name] = val.to_dict()
            else:
                if metacfg.meta_rootonly and self.chains:
                    continue
                dic[field.name] = val

        return dic

    @functools.cached_property
    def metainfo(self, pretty: bool = True) -> str:
        if pretty:
            return json.dumps(self.metainfo_dic, indent=4)
        else:
            return json.dumps(self.metainfo_dic, separators=(',', ':'))

    @functools.cached_property
    def hash_dic(self) -> dict:
        dic = {}

        for field in dcs.fields(self):
            metacfg = DataclsCfg(**field.metadata.get(DataclsCfg.KEY, {}))
            if metacfg.hash_ex:
                continue

            val = getattr(self, field.name)
            if hasattr(val, "to_dict"):
                dic[field.name] = val.to_dict()
            else:
                dic[field.name] = val

        return dic

    @functools.cached_property
    def hash(self) -> str:
        hashdic_bytes = json.dumps(self.hash_dic, separators=(',', ':')).encode('utf-8')
        hsh = hashlib.sha1(hashdic_bytes, usedforsecurity=False)
        return hsh.hexdigest()

    @property
    def shorthash(self) -> str:
        return self.hash[:8]

    @abc.abstractmethod
    @functools.cached_property
    def dirname(self) -> str:
        ...

    @functools.cached_property
    def dstdir(self) -> Path:
        node_cfg = get_node_cfg()
        return node_cfg.path.dataset / "playground" / self.dirname

    def dump_metainfo(self) -> None:
        with (self.dstdir / "metainfo.json").open('w', encoding='utf-8') as f:
            f.write(self.metainfo)
        append(self, self.dstdir)

    @abc.abstractmethod
    def run(self) -> None:
        ...
