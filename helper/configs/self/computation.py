import dataclasses
from pathlib import Path

from ..base import CfgBase


@dataclasses.dataclass
class ComputationCfg(CfgBase):
    base_dir: Path = dataclasses.field(default_factory=Path)
    render_dirs: Path = dataclasses.field(default_factory=Path)
    render_ref_dirs: Path = dataclasses.field(default_factory=Path)
    log_file_fstr: str = ''
    ref_log_file_fstr: str = ''

    @staticmethod
    def from_dict(d: dict) -> "ComputationCfg":
        return ComputationCfg(**d)
