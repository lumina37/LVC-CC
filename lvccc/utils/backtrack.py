from ..task import CodecTask, ConvertTask, TRetTask, TSelfTask, TVarTask


def get_ancestor(task: TSelfTask, cls: type[TRetTask]) -> TRetTask:
    for t in task.chain:
        if isinstance(t, cls):
            return t

    return cls()


def is_anchor(task: TVarTask) -> bool:
    return len(task.chain) > 1 and isinstance(task.chain[1], CodecTask)


def is_base(task: TVarTask) -> bool:
    return len(task.chain) > 1 and isinstance(task.chain[1], ConvertTask)
