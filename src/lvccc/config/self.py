import dataclasses as dcs
import tomllib
from pathlib import Path
from typing import BinaryIO

from .base import UpdateImpl


@dcs.dataclass
class _Dir(UpdateImpl):
    input: Path = dcs.field(default_factory=Path)
    output: Path = dcs.field(default_factory=Path)


@dcs.dataclass
class _App(UpdateImpl):
    ffmpeg: str = ""
    encoder: str = ""
    decoder: str = ""
    processor: str = ""
    convertor: str = ""


@dcs.dataclass
class Config(UpdateImpl):
    frames: int = 0
    views: int = 0
    seqs: list[str] = dcs.field(default_factory=list)
    dir: _Dir = dcs.field(default_factory=_Dir)
    app: _App = dcs.field(default_factory=_App)
    anchorQP: dict[str, list[int]] = dcs.field(default_factory=dict)
    proc: dict = dcs.field(default_factory=dict)

    @staticmethod
    def load(f: BinaryIO) -> "Config":
        return Config(**tomllib.load(f))

    @staticmethod
    def from_file(path: Path) -> "Config":
        with path.open("rb") as f:
            return Config.load(f)


def update_config(path: Path | str) -> Config:
    global _CFG
    path = Path(path)
    _CFG.update(Config.from_file(path))
    return _CFG


def get_config() -> Config:
    return _CFG


_CFG = Config.from_file(Path("config") / "default.toml")
