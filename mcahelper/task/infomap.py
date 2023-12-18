import json
from pathlib import Path
from typing import Any

from ..cfg.node import get_node_cfg
from .factory import TaskFactory

TpInfomap = dict[Any, Path]

INFOMAP: TpInfomap = None


def init_infomap() -> None:
    global INFOMAP

    node_cfg = get_node_cfg()

    INFOMAP = {}
    for d in (node_cfg.path.dataset / "playground").iterdir():
        metainfo_path = d / "metainfo.json"
        if not metainfo_path.exists():
            continue
        with metainfo_path.open('r', encoding='utf-8') as f:
            metainfo = json.load(f)
            task = TaskFactory(**metainfo)
            INFOMAP[task.hash] = metainfo_path.parent


def get_infomap() -> TpInfomap:
    global INFOMAP

    if INFOMAP is None:
        init_infomap()

    return INFOMAP


def query(task) -> Path:
    infomap = get_infomap()
    return infomap[task.hash]


def append(task, path: Path) -> None:
    infomap = get_infomap()
    infomap[task.hash] = path
