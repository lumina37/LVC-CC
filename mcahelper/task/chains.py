import dataclasses as dcs
from typing import SupportsIndex, overload

from pydantic.dataclasses import dataclass

from ..helper import DataclsCfg
from .factory import TaskFactory
from .typing import Marshalable


@dataclass
class Chains:
    objs: list = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.objs)

    @overload
    def __getitem__(self, idx: SupportsIndex) -> Marshalable: ...

    @overload
    def __getitem__(self, idx: slice) -> list[Marshalable]: ...

    def __getitem__(self, idx):
        return self.objs.__getitem__(idx)

    @staticmethod
    def unmarshal(objs: list[dict]) -> "Chains":
        objs = [TaskFactory(**d) for d in objs]
        chains = Chains(objs=objs)
        return chains

    def marshal(self) -> list[dict]:
        def exclude_if(field: dcs.Field) -> bool:
            if field.name == 'chains':
                return True
            if DataclsCfg.getval_from_meta(field.metadata, 'no_meta'):
                return True
            return False

        objs: list[Marshalable] = self.objs
        dics = [t.marshal(exclude_if) for t in objs]

        return dics

    def copy(self) -> "Chains":
        return Chains(self.objs.copy())
