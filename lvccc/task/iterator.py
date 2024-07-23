import json
from collections.abc import Callable, Generator

from ..config import get_config
from .base import TDerivedTask
from .chain import Chain
from .codec import CodecTask
from .preproc import PreprocTask
from .render import RenderTask


def tasks(
    cls: type[TDerivedTask] = None, require: Callable[[TDerivedTask], bool] | None = lambda _: True
) -> Generator[TDerivedTask]:
    config = get_config()

    tasks_dir = config.path.output / "tasks"
    glob_pattern = f"{cls.task}*" if cls is not None else '*'
    for d in tasks_dir.glob(glob_pattern):
        if not d.is_dir():
            continue

        taskinfo_path = d / "task.json"
        if not taskinfo_path.exists():
            continue

        with taskinfo_path.open(encoding='utf-8') as f:
            taskinfo = json.load(f)
            chain = Chain(taskinfo)
            task = chain[-1]
            if not require(task):
                continue
            yield task


def get_codec_task(task: TDerivedTask) -> CodecTask:
    for t in task.chain:
        if isinstance(t, CodecTask):
            return t

    return CodecTask()


def has_mca(task: TDerivedTask) -> bool:
    return len(task.chain) > 1 and task.chain.objs[1]['task'] == PreprocTask.task


def is_anchor(task: TDerivedTask) -> bool:
    return len(task.chain) == 1 and task.task == RenderTask.task
