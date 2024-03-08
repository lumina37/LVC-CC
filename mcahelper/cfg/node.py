from io import IOBase
from pathlib import Path

import tomllib
from pydantic.dataclasses import dataclass

from ..logging import get_logger


@dataclass
class _Cases:
    vtm_types: list[str]
    seqs: list[str]


@dataclass
class _Path:
    dataset: Path


@dataclass
class _App:
    ffmpeg: str
    encoder: str
    preproc: str
    postproc: str
    rlc: str


@dataclass
class NodeCfg:
    frames: int
    cases: _Cases
    path: _Path
    app: _App


_NODE_CFG = None


def load(f: IOBase) -> NodeCfg:
    return NodeCfg(**tomllib.load(f))


def from_file(path: Path) -> NodeCfg:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)


def set_node_cfg(path: Path) -> NodeCfg:
    global _NODE_CFG
    _NODE_CFG = from_file(path)
    return _NODE_CFG


def get_node_cfg() -> NodeCfg | None:
    if _NODE_CFG is None:
        log = get_logger()
        msg = "You should call `set_node_cfg` first!"
        log.critical(msg)
        raise RuntimeError(msg)

    return _NODE_CFG
