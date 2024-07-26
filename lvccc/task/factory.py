from .abc import ProtoTask

_TASKMAP = {}


def register(task_tp: type[ProtoTask]):
    global _TASKMAP
    _TASKMAP[task_tp.task] = task_tp


def get_task_type(task_name) -> type[ProtoTask]:
    return _TASKMAP[task_name]
