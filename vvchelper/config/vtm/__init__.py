import dataclasses
from io import TextIOBase
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class VTMCfg(CfgBase):
    InputFile: str
    InputBitDepth: int
    FrameRate: int
    FrameSkip: int
    SourceWidth: int
    SourceHeight: int
    FramesToBeEncoded: int
    ConformanceMode: int
    Level: float

    def dump(self, f: TextIOBase) -> None:
        f.writelines(f"{k}: {v}\n" for k, v in dataclasses.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIOBase) -> "VTMCfg":
        def _items():
            for row in f.readlines():
                pound_idx = row.find('#')
                if pound_idx != -1:
                    row = row[:pound_idx]

                key, _, value = row.partition(':')
                if not value:
                    continue

                key = key.strip()
                value = value.strip()

                yield key, value

        return VTMCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "VTMCfg":
        with path.open('r') as f:
            return VTMCfg.load(f)
