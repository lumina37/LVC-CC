import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class PostprocessCfg(CfgBase):
    program: Path = dataclasses.field(default_factory=Path)
    param_file: Path = dataclasses.field(default_factory=Path)
    calibration_file: Path = dataclasses.field(default_factory=Path)
    temp_param_file: Path = dataclasses.field(default_factory=Path)
    src_dirs: Path = dataclasses.field(default_factory=Path)
    dst_dir_fstr: str = ""

    @staticmethod
    def from_dict(d: dict) -> "PostprocessCfg":
        return PostprocessCfg(**d)
