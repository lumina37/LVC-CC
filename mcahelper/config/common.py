from io import IOBase
from pathlib import Path

import tomllib
from pydantic.dataclasses import dataclass


@dataclass
class _QP:
    wMCA: dict[str, list[int]]
    woMCA: dict[str, list[int]]


@dataclass
class _DefaultPattern:
    py: str
    c: str


@dataclass
class CommonCfg:
    QP: _QP
    default_pattern: _DefaultPattern
    pattern: dict[str, str]
    start_idx: dict[str, int]


_COMMON_CFG = None


def load(f: IOBase) -> CommonCfg:
    return CommonCfg(**tomllib.load(f))


def from_file(path: Path) -> CommonCfg:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)


def set_common_cfg(path: Path) -> CommonCfg:
    global _COMMON_CFG
    _COMMON_CFG = from_file(path)
    return _COMMON_CFG


def get_common_cfg() -> CommonCfg | None:
    return _COMMON_CFG
