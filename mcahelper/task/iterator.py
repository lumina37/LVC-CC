import json
from collections.abc import Callable, Generator
from typing import Any, Optional

from ..cfg.node import get_node_cfg
from .base import BaseTask
from .factory import TaskFactory


def tasks(cls: Any = None, require: Optional[Callable[[BaseTask], bool]] = lambda _: True) -> Generator[BaseTask]:
    node_cfg = get_node_cfg()

    playground_path = node_cfg.path.dataset / "playground"
    glob_pattern = f"{cls.task}*" if cls is not None else '*'
    for d in playground_path.glob(glob_pattern):
        if not d.is_dir():
            continue

        metainfo_path = d / "metainfo.json"
        if not metainfo_path.exists():
            continue

        with metainfo_path.open('r', encoding='utf-8') as f:
            metainfo = json.load(f)
            task = TaskFactory(**metainfo)
            if not require(task):
                continue
            yield task
