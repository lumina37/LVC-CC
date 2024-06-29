import dataclasses as dcs
from typing import SupportsIndex

from pydantic.dataclasses import dataclass

from .factory import get_task_type


@dataclass
class Chain:
    objs: list[dict] = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.objs)

    def __getitem__(self, idx: SupportsIndex):
        dic = self.objs[idx]
        TaskType = get_task_type(dic['task'])
        item = TaskType(**dic)
        item.chain.objs = self.objs[:idx]
        return item

    def copy(self) -> "Chain":
        return Chain(self.objs.copy())
