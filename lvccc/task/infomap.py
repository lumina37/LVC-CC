import json
from pathlib import Path

from ..config import get_config
from .abc import TVarTask
from .chain import Chain

TypeInfomap = dict[int, Path]

_INFOMAP: TypeInfomap = None


def gen_infomap(tasks_dir: Path) -> TypeInfomap:
    infomap = {}
    if tasks_dir.is_dir():
        for task_dir in tasks_dir.iterdir():
            taskinfo_path = task_dir / "task.json"
            if not taskinfo_path.exists():
                continue
            with taskinfo_path.open(encoding='utf-8') as f:
                objs = json.load(f)
                chain = Chain(objs)
                task = chain[-1]
                infomap[task.hash] = task_dir.absolute()

    return infomap


def get_infomap() -> TypeInfomap:
    global _INFOMAP

    if _INFOMAP is None:
        config = get_config()
        _INFOMAP = gen_infomap(config.path.output / "tasks")

    return _INFOMAP


def query(task: TVarTask) -> Path | None:
    infomap = get_infomap()
    path = infomap.get(task.hash, None)
    return path


def append(task: TVarTask, path: Path) -> None:
    infomap = get_infomap()
    infomap[task.hash] = path
