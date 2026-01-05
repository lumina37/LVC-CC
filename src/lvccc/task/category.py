from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .abc import ProtoTask

_CONVERT_TASK_NAMES = set()


def reg_convert_task_type(task_type: type[ProtoTask]) -> None:
    global _CONVERT_TASK_NAMES
    _CONVERT_TASK_NAMES.add(task_type.task)


def is_convert_task(task_name: str) -> bool:
    return task_name in _CONVERT_TASK_NAMES
