import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class Raw2PNGCfg(CfgBase):
    param_file: Path = dataclasses.field(default_factory=Path)
    src_file: Path = dataclasses.field(default_factory=Path)
    dst_dir: Path = dataclasses.field(default_factory=Path)

    @staticmethod
    def from_dict(d: dict) -> "Raw2PNGCfg":
        return Raw2PNGCfg(**d)
