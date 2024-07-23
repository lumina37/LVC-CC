import json
from pathlib import Path

from ..config import get_config
from ..utils import mkdir
from .chain import Chain

TypeInfomap = dict[str, Path]

_INFOMAP: TypeInfomap = None


def init_infomap() -> TypeInfomap:
    config = get_config()

    tasks_dir = config.path.output / "tasks"
    mkdir(tasks_dir)

    infomap = {}
    for d in tasks_dir.iterdir():
        taskinfo_path = d / "task.json"
        if not taskinfo_path.exists():
            continue
        with taskinfo_path.open(encoding='utf-8') as f:
            taskinfo = json.load(f)
            chains = Chain(taskinfo)
            task = chains[-1]
            infomap[task.hash] = taskinfo_path.parent

    return infomap


def register_infomap(infomap: TypeInfomap) -> None:
    global _INFOMAP
    _INFOMAP = infomap


def get_infomap() -> TypeInfomap:
    global _INFOMAP

    if _INFOMAP is None:
        _INFOMAP = init_infomap()

    return _INFOMAP


def query(task) -> Path | None:
    infomap = get_infomap()
    path = infomap.get(task.hash, None)
    return path


def append(task, path: Path) -> None:
    infomap = get_infomap()
    infomap[task.hash] = path
