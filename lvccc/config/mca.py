import dataclasses as dcs
import math
from pathlib import Path
from typing import TextIO

from .base import AutoConvImpl


@dcs.dataclass
class MCACfg(AutoConvImpl):
    pipeline: int = 0
    calibFile: str = ""
    inFile: str = ""
    outDir: str = ""
    frameBegin: int = 0
    frameEnd: int = 0
    height: int = 2048
    width: int = 2048
    crop_ratio: float = 1 / math.sqrt(2)

    def dump(self, f: TextIO) -> None:
        maxlen = 0
        for field in dcs.fields(self):
            if (flen := len(field.name)) > maxlen:
                maxlen = flen

        fstr = f"{{k:<{maxlen+2}}}{{v}}\n"
        f.writelines(fstr.format(k=k, v=v) for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIO) -> "MCACfg":
        fields = {field.name for field in dcs.fields(MCACfg)}

        def _items():
            for row in f:
                key, value = row.replace('\t', ' ').split(' ', maxsplit=1)
                value = value.lstrip().rstrip('\n')
                if key not in fields:
                    continue
                yield key, value

        return MCACfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w', encoding='utf-8') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "MCACfg":
        with path.open(encoding='utf-8') as f:
            return MCACfg.load(f)
