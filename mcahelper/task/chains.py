import dataclasses as dcs
import functools
from typing import Protocol, SupportsIndex, overload

from pydantic.dataclasses import dataclass

from .factory import TaskFactory


@dataclass
class HasDic(Protocol):
    @functools.cached_property
    def dic(self) -> dict: ...


@dataclass
class Chains:
    tasks: list = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.tasks)

    @overload
    def __getitem__(self, idx: SupportsIndex) -> HasDic: ...

    @overload
    def __getitem__(self, idx: slice) -> list[HasDic]: ...

    def __getitem__(self, idx):
        return self.tasks.__getitem__(idx)

    @staticmethod
    def from_dict(dic: dict) -> "Chains":
        tasks = [TaskFactory(**d) for d in dic]
        chains = Chains(tasks=tasks)
        return chains

    def to_dict(self) -> list[dict]:
        return [t.dic for t in self.tasks]

    def copy(self) -> "Chains":
        return Chains(self.tasks.copy())
