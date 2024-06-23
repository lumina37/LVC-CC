import dataclasses as dcs
from io import TextIOBase
from pathlib import Path

from pydantic.dataclasses import dataclass


@dataclass
class RLCCfg:
    viewNum: int = 5
    rmode: int = 1
    pmode: int = 0
    mmode: int = 2
    lmode: int = 1
    Calibration_xml: str = ""
    RawImage_Path: str = ""
    Output_Path: str = ""
    Debayer_mode: int = 0
    Isfiltering: int = 0
    isCLAHE: int = 0
    Gamma: float = 1.0
    Lambda: float = 0.05
    Sigma: int = 0
    input_model: int = 0
    output_model: int = 0
    start_frame: int = 1
    end_frame: int = 1
    height: int = 2048
    width: int = 2048

    def dump(self, f: TextIOBase) -> None:
        f.writelines(f"{k}\t{v}\n" for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIOBase) -> "RLCCfg":
        def _items():
            for row in f.readlines():
                key, value = row.replace('\t', ' ').split(' ', maxsplit=1)
                value = value.lstrip().rstrip('\n')
                yield key, value

        return RLCCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "RLCCfg":
        with path.open('r') as f:
            return RLCCfg.load(f)
