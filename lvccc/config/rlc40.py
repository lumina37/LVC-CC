import dataclasses as dcs
import math
from pathlib import Path
from typing import TextIO

from .base import AutoConvImpl


@dcs.dataclass
class RLC40Cfg(AutoConvImpl):
    pipeline: int = 1
    viewNum: int = 5
    Calibration_xml: str = ""
    RawImage_Path: str = ""
    Output_Path: str = ""
    start_frame: int = 1
    end_frame: int = 1
    height: int = 2048
    width: int = 2048
    upsample: int = 2
    psizeInflate: float = math.sqrt(3) * 1.5
    maxPsize: float = 0.5
    patternSize: float = 0.3
    psizeShortcutThreshold: int = 4

    def dump(self, f: TextIO) -> None:
        maxlen = 0
        for field in dcs.fields(self):
            if (flen := len(field.name)) > maxlen:
                maxlen = flen

        fstr = f"{{k:<{maxlen + 2}}}{{v}}\n"
        f.writelines(fstr.format(k=k, v=v) for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIO) -> "RLC40Cfg":
        def _items():
            for row in f:
                key, value = row.replace("\t", " ").split(" ", maxsplit=1)
                value = value.lstrip().rstrip("\n")
                yield key, value

        return RLC40Cfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open("w") as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "RLC40Cfg":
        with path.open(encoding="utf-8") as f:
            return RLC40Cfg.load(f)
