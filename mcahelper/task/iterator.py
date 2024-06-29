import json
from collections.abc import Callable, Generator
from typing import Any

from ..config.node import get_node_cfg
from .base import BaseTask
from .chain import Chain


def tasks(cls: Any = None, require: Callable[[BaseTask], bool] | None = lambda _: True) -> Generator[BaseTask]:
    node_cfg = get_node_cfg()

    playground_path = node_cfg.path.dataset / "playground"
    glob_pattern = f"{cls.task}*" if cls is not None else '*'
    for d in playground_path.glob(glob_pattern):
        if not d.is_dir():
            continue

        taskinfo_path = d / "task.json"
        if not taskinfo_path.exists():
            continue

        with taskinfo_path.open('r', encoding='utf-8') as f:
            taskinfo = json.load(f)
            chain = Chain(taskinfo)
            task = chain[-1]
            if not require(task):
                continue
            yield task
