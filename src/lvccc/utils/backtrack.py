from __future__ import annotations

from ..task import EncodeTask, ProtoTask


def ancestor_with_spec_type[T](task: ProtoTask, cls: type[T]) -> T:
    for idx, task_dict in enumerate(task.chain):
        if task_dict["task"] == cls.task:
            return task.ancestor(idx)

    return cls()


def is_anchor(task: ProtoTask) -> bool:
    return len(task.chain) > 1 and task.chain[1]["task"] == EncodeTask.task


def is_base(task: ProtoTask) -> bool:
    return len(task.chain) > 1 and task.chain[1]["task"].startswith("convert")
