from __future__ import annotations

import dataclasses as dcs
from pathlib import Path
from typing import BinaryIO

import tomllib
from pydantic.dataclasses import dataclass


@dataclass
class _UpdateImpl:
    def update(self, rhs: _UpdateImpl) -> _UpdateImpl:
        for field in dcs.fields(rhs):
            rhs_value = getattr(rhs, field.name)
            if not rhs_value:
                continue
            if hasattr(rhs_value, 'update'):
                lhs_value = getattr(self, field.name)
                lhs_value.update(rhs_value)
            else:
                setattr(self, field.name, rhs_value)


@dataclass
class _Cases(_UpdateImpl):
    vtm_types: list[str] = dcs.field(default_factory=list)
    seqs: list[str] = dcs.field(default_factory=list)


@dataclass
class _Path(_UpdateImpl):
    input: Path = dcs.field(default_factory=Path)
    output: Path = dcs.field(default_factory=Path)
    pattern: dict[str, str] = dcs.field(default_factory=dict)


@dataclass
class _App(_UpdateImpl):
    ffmpeg: str = ""
    encoder: str = ""
    preproc: str = ""
    postproc: str = ""
    rlc: str = ""


@dataclass
class _QP(_UpdateImpl):
    wMCA: dict[str, list[int]] = dcs.field(default_factory=dict)
    woMCA: dict[str, list[int]] = dcs.field(default_factory=dict)


@dataclass
class Config(_UpdateImpl):
    frames: int = 0
    cases: _Cases = dcs.field(default_factory=_Cases)
    path: _Path = dcs.field(default_factory=_Path)
    app: _App = dcs.field(default_factory=_App)
    default_pattern: str = ""
    QP: _QP = dcs.field(default_factory=_QP)
    start_idx: dict[str, int] = dcs.field(default_factory=dict)


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
