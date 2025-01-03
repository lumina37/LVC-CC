import dataclasses as dcs
from pathlib import Path
from typing import BinaryIO

import tomllib

from .base import UpdateImpl


@dcs.dataclass
class _Cases(UpdateImpl):
    vtm_types: list[str] = dcs.field(default_factory=list)
    seqs: list[str] = dcs.field(default_factory=list)


@dcs.dataclass
class _Path(UpdateImpl):
    input: Path = dcs.field(default_factory=Path)
    output: Path = dcs.field(default_factory=Path)


@dcs.dataclass
class _App(UpdateImpl):
    encoder: str = ""
    proccessor: str = ""
    convertor: str = ""


@dcs.dataclass
class _QP(UpdateImpl):
    wMCA: dict[str, list[int]] = dcs.field(default_factory=dict)
    anchor: dict[str, list[int]] = dcs.field(default_factory=dict)


@dcs.dataclass
class Config(UpdateImpl):
    frames: int = 1
    views: int = 5
    cases: _Cases = dcs.field(default_factory=_Cases)
    path: _Path = dcs.field(default_factory=_Path)
    app: _App = dcs.field(default_factory=_App)
    default_pattern: str = ""
    QP: _QP = dcs.field(default_factory=_QP)


def load(f: BinaryIO) -> Config:
    return Config(**tomllib.load(f))


def from_file(path: Path) -> Config:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)


def update_config(path: Path) -> Config:
    global _CFG
    _CFG.update(from_file(path))
    return _CFG


def get_config() -> Config:
    return _CFG


_CFG = from_file(Path('config') / 'default.toml')
