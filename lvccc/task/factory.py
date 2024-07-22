_TASKMAP = {}


def register(task_tp):
    global _TASKMAP
    _TASKMAP[task_tp.task] = task_tp


def get_task_type(task_name):
    return _TASKMAP[task_name]
