import dataclasses as dcs
from pathlib import Path
from typing import TextIO

from .rlc40 import RLC40Cfg


@dcs.dataclass
class RLC45Cfg(RLC40Cfg):
    Output_format: str = "yuv"

    @staticmethod
    def load(f: TextIO) -> "RLC45Cfg":
        def _items():
            for row in f:
                key, value = row.replace("\t", " ").split(" ", maxsplit=1)
                value = value.lstrip().rstrip("\n")
                yield key, value

        return RLC45Cfg(**dict(_items()))

    @staticmethod
    def from_file(path: Path) -> "RLC45Cfg":
        with path.open(encoding="utf-8") as f:
            return RLC45Cfg.load(f)
