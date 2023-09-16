import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class Dec2PNGCfg(CfgBase):
    size_ref_img_file: Path = dataclasses.field(default_factory=Path)
    src_file_pattern: str = ""
    dst_dir_fstr: str = ""

    @staticmethod
    def from_dict(d: dict) -> "Dec2PNGCfg":
        return Dec2PNGCfg(**d)
