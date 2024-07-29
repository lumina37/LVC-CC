from __future__ import annotations

import dataclasses as dcs
from typing import SupportsIndex

from pydantic.dataclasses import dataclass

from ..helper import to_json
from .abc import ProtoTask
from .factory import get_task_type


@dataclass
class Chain:
    objs: list[dict] = dcs.field(default_factory=list)

    def __len__(self) -> int:
        return len(self.objs)

    def __getitem__(self, idx: SupportsIndex) -> ProtoTask:
        fields = self.objs[idx]
        TaskType = get_task_type(fields['task'])
        task: ProtoTask = TaskType.deserialize(fields)
        task.chain.objs = self.objs[:idx]
        return task

    def copy(self) -> Chain:
        return Chain(self.objs.copy())

    def to_json(self, pretty: bool = False) -> str:
        for i, task in enumerate(self):
            task: ProtoTask = task
            self.objs[i] = task.fields
        return to_json(self.objs, pretty)
