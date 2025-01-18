from __future__ import annotations

from ..task import CodecTask, ConvertTask, ProtoTask


def get_ancestor(task: ProtoTask, cls: type[ProtoTask]) -> ProtoTask:
    for t in task.chain:
        if isinstance(t, cls):
            return t

    return cls()


def is_anchor(task: ProtoTask) -> bool:
    return len(task.chain) > 1 and isinstance(task.chain[1], CodecTask)


def is_base(task: ProtoTask) -> bool:
    return len(task.chain) > 1 and isinstance(task.chain[1], ConvertTask)
