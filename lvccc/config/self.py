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
    input: Path
    output: Path
    pattern: dict[str, str]


@dataclass
class _App:
    ffmpeg: str
    encoder: str
    preproc: str
    postproc: str
    rlc: str


@dataclass
class _QP:
    wMCA: dict[str, list[int]]
    woMCA: dict[str, list[int]]


@dataclass
class Config:
    frames: int
    cases: _Cases
    path: _Path
    app: _App
    QP: _QP
    start_idx: dict[str, int]


_CFG = None


def load(f: IOBase) -> Config:
    return Config(**tomllib.load(f))


def from_file(path: Path) -> Config:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)


def set_config(path: Path) -> Config:
    global _CFG
    _CFG = from_file(path)
    return _CFG


def get_config() -> Config | None:
    if _CFG is None:
        log = get_logger()
        msg = "You should call `set_config` first!"
        log.critical(msg)
        raise RuntimeError(msg)
    return _CFG
