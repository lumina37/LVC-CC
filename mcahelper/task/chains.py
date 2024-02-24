import dataclasses as dcs
from typing import SupportsIndex

from pydantic.dataclasses import dataclass

from ..helper import DataclsCfg
from .factory import TaskFactory
from .typing import Marshalable


@dataclass
class Chains:
    objs: list = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.objs)

    def __getitem__(self, idx: SupportsIndex) -> Marshalable:
        item = self.objs[idx]
        item.chains.objs = self.objs[:idx]
        return item

    @staticmethod
    def unmarshal(objs: list[dict]) -> "Chains":
        objs = [TaskFactory(**d) for d in objs]
        chains = Chains(objs=objs)
        return chains

    def marshal(self) -> list[dict]:
        def exclude_if(field: dcs.Field) -> bool:
            if field.name == 'chains':
                return True
            if DataclsCfg.from_meta(field.metadata).no_meta:
                return True
            return False

        objs: list[Marshalable] = self.objs
        dics = [t.marshal(exclude_if) for t in objs]

        return dics

    def copy(self) -> "Chains":
        return Chains(self.objs.copy())
