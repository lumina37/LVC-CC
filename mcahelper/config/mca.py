import dataclasses as dcs
import math
from io import TextIOBase
from pathlib import Path

from pydantic.dataclasses import dataclass


@dataclass
class MCACfg:
    camType: int = 0
    Calibration_xml: str = ""
    RawImage_Path: str = ""
    Output_Path: str = ""
    start_frame: int = 1
    end_frame: int = 1
    height: int = 2048
    width: int = 2048
    crop_ratio: float = 1 / math.sqrt(2)

    def dump(self, f: TextIOBase) -> None:
        f.writelines(f"{k}\t{v}\n" for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIOBase) -> "MCACfg":
        def _items():
            for row in f.readlines():
                key, value = row.replace('\t', ' ').split(' ', maxsplit=1)
                value = value.lstrip().rstrip('\n')
                yield key, value

        return MCACfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "MCACfg":
        with path.open('r') as f:
            return MCACfg.load(f)
