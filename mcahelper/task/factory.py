_TASKMAP = {}


def register(task_tp):
    global _TASKMAP
    _TASKMAP[task_tp.task_name] = task_tp


class TaskFactory:
    def __new__(cls, **kwargs):
        realcls = _TASKMAP[kwargs.pop('task')]
        return realcls.from_dict(kwargs)
