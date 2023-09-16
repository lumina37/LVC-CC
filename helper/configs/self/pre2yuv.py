import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class Pre2YUVCfg(CfgBase):
    param_file: Path = dataclasses.field(default_factory=Path)
    src_dir: Path = dataclasses.field(default_factory=Path)
    dst_file: Path = dataclasses.field(default_factory=Path)

    @staticmethod
    def from_dict(d: dict) -> "Pre2YUVCfg":
        return Pre2YUVCfg(**d)
