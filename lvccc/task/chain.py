from __future__ import annotations

import dataclasses as dcs
from typing import SupportsIndex, overload

from pydantic.dataclasses import dataclass

from ..helper import to_json
from .abc import ProtoTask
from .factory import get_task_type


@dataclass
class Chain:
    objs: list[dict] = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.objs)

    @overload
    def __getitem__(self, idx: SupportsIndex) -> ProtoTask: ...

    @overload
    def __getitem__(self, idx: slice) -> Chain: ...

    def __getitem__(self, idx):
        if isinstance(idx, int):
            TaskType = get_task_type(self.objs[idx]['task'])
            endidx = len(self.objs) if idx == -1 else idx + 1
            task: ProtoTask = TaskType.deserialize(self.objs[:endidx])
            return task
        else:
            return Chain(self.objs[idx])

    def copy(self) -> Chain:
        return Chain(self.objs.copy())

    def to_json(self, pretty: bool = False) -> str:
        for i, task in enumerate(self):
            task: ProtoTask = task
            self.objs[i] = task.fields()
        return to_json(self.objs, pretty)
