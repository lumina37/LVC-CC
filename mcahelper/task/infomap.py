import json
import multiprocessing as mp
from pathlib import Path

from ..cfg.node import get_node_cfg
from .factory import TaskFactory

_INFOMAP_MANAGER = None
_INFOMAP_LOCK = mp.Lock()
_INFOMAP = None


def init_infomap() -> None:
    node_cfg = get_node_cfg()

    global _INFOMAP_MANAGER
    global _INFOMAP

    _INFOMAP_MANAGER = mp.Manager()
    _INFOMAP = _INFOMAP_MANAGER.dict()

    for d in (node_cfg.path.dataset / "playground").iterdir():
        metainfo_path = d / "metainfo.json"
        if not metainfo_path.exists():
            continue
        with metainfo_path.open('r', encoding='utf-8') as f:
            metainfo = json.load(f)
            task = TaskFactory(**metainfo)
            _INFOMAP[task.hash] = metainfo_path.parent


def get_infomap():
    global _INFOMAP

    if _INFOMAP is None:
        init_infomap()

    return _INFOMAP


def query(task) -> Path:
    with _INFOMAP_LOCK:
        infomap = get_infomap()
        path = infomap[task.hash]
    return path


def append(task, path: Path) -> None:
    with _INFOMAP_LOCK:
        infomap = get_infomap()
        infomap[task.hash] = path
