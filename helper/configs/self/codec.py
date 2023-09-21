import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class CodecCfg(CfgBase):
    ctcqp: dict = dataclasses.field(default_factory=dict)
    program: Path = dataclasses.field(default_factory=Path)
    encode_mode_cfg_file: Path = dataclasses.field(default_factory=Path)
    param_file: Path = dataclasses.field(default_factory=Path)
    size_ref_img_file: Path = dataclasses.field(default_factory=Path)
    src_file: Path = dataclasses.field(default_factory=Path)
    dst_file_fstr: str = ""
    log_file_fstr: str = ""
    recon_file_fstr: str = ""

    @staticmethod
    def from_dict(d: dict) -> "CodecCfg":
        return CodecCfg(**d)
