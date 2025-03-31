from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from ..config import get_config
from ..logging import get_logger
from .base import BaseTask

if TYPE_CHECKING:
    from .abc import ProtoTask

TypeInfomap = dict[int, Path]

_INFOMAP: TypeInfomap = None


def gen_infomap(tasks_dir: Path) -> TypeInfomap:
    infomap = {}
    if tasks_dir.is_dir():
        logger = get_logger()
        for task_dir in tasks_dir.iterdir():
            taskinfo_path = task_dir / "task.json"
            if not taskinfo_path.exists():
                continue
            with taskinfo_path.open(encoding="utf-8") as f:
                try:
                    chain = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to load task info from: {taskinfo_path}")
                    continue
                task = BaseTask.from_dicts(chain)
                infomap[task.hash] = task_dir.absolute()

    return infomap


def get_infomap() -> TypeInfomap:
    global _INFOMAP

    if _INFOMAP is None:
        config = get_config()
        _INFOMAP = gen_infomap(config.dir.output / "tasks")

    return _INFOMAP


def query(task: ProtoTask) -> Path | None:
    infomap = get_infomap()
    path = infomap.get(task.hash, None)
    return path


def append(task: ProtoTask, path: Path) -> None:
    infomap = get_infomap()
    infomap[task.hash] = path
