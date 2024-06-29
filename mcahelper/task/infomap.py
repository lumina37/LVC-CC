import json
from pathlib import Path

from ..config.node import get_node_cfg
from ..helper import mkdir
from .chain import Chain

TypeInfomap = dict[str, Path]

_INFOMAP: TypeInfomap = None


def init_infomap() -> TypeInfomap:
    node_cfg = get_node_cfg()

    playground_dir = node_cfg.path.dataset / "playground"
    mkdir(playground_dir)

    infomap = {}
    for d in playground_dir.iterdir():
        taskinfo_path = d / "task.json"
        if not taskinfo_path.exists():
            continue
        with taskinfo_path.open('r', encoding='utf-8') as f:
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
