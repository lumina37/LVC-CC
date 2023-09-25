import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class BaseRenderCfg(CfgBase):
    program: Path = dataclasses.field(default_factory=Path)
    param_file: Path = dataclasses.field(default_factory=Path)
    calibration_file: Path = dataclasses.field(default_factory=Path)
    src_dir: Path = dataclasses.field(default_factory=Path)
    dst_dir: Path = dataclasses.field(default_factory=Path)

    @staticmethod
    def from_dict(d: dict) -> "BaseRenderCfg":
        return BaseRenderCfg(**d)
