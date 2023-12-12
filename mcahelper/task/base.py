import abc
import functools
import hashlib
import json
import pickle
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Optional

from dataclasses_json import Undefined, config, dataclass_json

from ..cfg.node import get_node_cfg


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class BaseTask:
    task_name: ClassVar[str] = "null"

    timestamp: int = field(
        default_factory=time.time_ns, hash=False, metadata=config(exclude=lambda _: True), kw_only=True
    )
    pretask: Optional["BaseTask"] = field(
        default=None, repr=False, hash=False, metadata=config(exclude=lambda _: True), kw_only=True
    )
    chains: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if pretask := self.pretask:
            chains = pretask.chains.copy()
            pretask_dic = {'task': pretask.task_name}
            pretask_dic.update(pretask.to_dict())
            pretask_dic.pop('chains')
            chains.append(pretask_dic)
            self.chains = chains

    @property
    def metainfo(self, pretty: bool = True) -> str:
        dic = {'task': self.task_name, 'time': self.timestamp}
        dic.update(self.to_dict())
        if pretty:
            return json.dumps(dic, indent=4)
        else:
            return json.dumps(dic, separators=(',', ':'))

    @functools.cached_property
    def hash(self) -> str:
        dic = self.to_dict()
        hsh = hashlib.sha1(pickle.dumps(dic), usedforsecurity=False)
        hsh.update(self.task_name.encode('utf-8'))
        hsh = hsh.hexdigest()
        return hsh

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

    @abc.abstractmethod
    def run(self) -> None:
        ...
