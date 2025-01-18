from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .abc import ProtoTask

_TASKMAP = {}


def reg_task_type(task_type: type[ProtoTask]):
    global _TASKMAP
    _TASKMAP[task_type.task] = task_type


def get_task_type(task_name: str) -> type[ProtoTask]:
    return _TASKMAP[task_name]
