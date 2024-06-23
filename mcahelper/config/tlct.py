import dataclasses as dcs
from io import TextIOBase
from pathlib import Path

from pydantic.dataclasses import dataclass


@dataclass
class TLCTCfg:
    pipeline: int = 1
    viewNum: int = 5
    rmode: int = 1
    Calibration_xml: str = ""
    RawImage_Path: str = ""
    Output_Path: str = ""
    start_frame: int = 1
    end_frame: int = 1
    height: int = 2048
    width: int = 2048

    def dump(self, f: TextIOBase) -> None:
        f.writelines(f"{k}\t{v}\n" for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIOBase) -> "TLCTCfg":
        def _items():
            for row in f.readlines():
                key, value = row.replace('\t', ' ').split(' ', maxsplit=1)
                value = value.lstrip().rstrip('\n')
                yield key, value

        return TLCTCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "TLCTCfg":
        with path.open('r') as f:
            return TLCTCfg.load(f)
