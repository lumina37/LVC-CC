from __future__ import annotations

import dataclasses as dcs
from typing import TYPE_CHECKING, SupportsIndex, overload

from .factory import get_task_type

if TYPE_CHECKING:
    from .abc import ProtoTask


@dcs.dataclass
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
            TaskType = get_task_type(self.objs[idx]["task"])
            endidx = len(self.objs) if idx == -1 else idx + 1
            task: ProtoTask = TaskType.from_dicts(self.objs[:endidx])
            return task
        else:
            return Chain(self.objs[idx])

    def copy(self) -> Chain:
        return Chain(self.objs.copy())
