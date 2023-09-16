import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class PreprocessCfg(CfgBase):
    program: Path = dataclasses.field(default_factory=Path)
    param_file: Path = dataclasses.field(default_factory=Path)
    calibration_file: Path = dataclasses.field(default_factory=Path)
    temp_param_file: Path = dataclasses.field(default_factory=Path)
    src_dir: Path = dataclasses.field(default_factory=Path)
    dst_dir: Path = dataclasses.field(default_factory=Path)

    @staticmethod
    def from_dict(d: dict) -> "PreprocessCfg":
        return PreprocessCfg(**d)
