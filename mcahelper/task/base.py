import abc
import copy
import dataclasses as dcs
import functools
import hashlib
import json
from pathlib import Path
from typing import Optional

from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from ..helper import DataclsCfg
from .chains import Chains
from .infomap import append


@dataclass
class BaseTask:
    task: str = ""
    seq_name: str = ""

    pretask: Optional["BaseTask"] = dcs.field(default=None, hash=False, kw_only=True)
    posttasks: list["BaseTask"] = dcs.field(default_factory=list, hash=False, kw_only=True)
    chains: Chains = dcs.field(default_factory=Chains, metadata=DataclsCfg(ex_if_empty=True).to_dict())

    def __post_init__(self) -> None:
        if pretask := self.pretask:
            chains = pretask.chains.copy()
            pretask = copy.copy(pretask)
            pretask.chains = Chains()
            chains.tasks.append(pretask)
            self.chains = chains

    @classmethod
    def from_dict(cls, dic: dict):
        if 'chains' in dic:
            dic['chains'] = Chains.from_dict(dic['chains'])
        kwargs = {field.name: val for field in dcs.fields(cls) if field.init and (val := dic.get(field.name, None))}
        return cls(**kwargs)

    @functools.cached_property
    def dic(self) -> dict:
        dic = {}

        for field in dcs.fields(self):
            if field.hash is False:
                continue

            metacfg = DataclsCfg(**field.metadata.get(DataclsCfg.KEY, {}))

            val = getattr(self, field.name)

            if metacfg.ex_if_empty and len(val) == 0:
                continue

            if hasattr(val, "to_dict"):
                dic[field.name] = val.to_dict()
            else:
                dic[field.name] = val

        return dic

    @functools.cached_property
    def metainfo(self, pretty: bool = True) -> str:
        if pretty:
            return json.dumps(self.dic, indent=4)
        else:
            return json.dumps(self.dic, separators=(',', ':'))

    @functools.cached_property
    def hash(self) -> str:
        hashdic_bytes = json.dumps(self.dic, separators=(',', ':')).encode('utf-8')
        hsh = hashlib.sha1(hashdic_bytes, usedforsecurity=False)
        return hsh.hexdigest()

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
        append(self, self.dstdir)

    @abc.abstractmethod
    def run(self) -> None: ...
