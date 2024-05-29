import functools
import math
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import MCACfg
from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask


@dataclass
class PreprocTask(BaseTask):
    task: str = "preproc"

    frames: int = 30
    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.crop_ratio:.3f}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        node_cfg = get_node_cfg()
        srcdir = node_cfg.path.dataset / "img" / self.seq_name
        return srcdir

    def _run(self) -> None:
        common_cfg = get_common_cfg()
        node_cfg = get_node_cfg()

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        shutil.copy(cfg_srcdir / "calibration.xml", cfg_dstdir)

        # Make dst dir
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        # Mod and write `mca.cfg`
        mcacfg_srcpath = cfg_srcdir / "mca.cfg"
        mcacfg = MCACfg.from_file(mcacfg_srcpath)

        mcacfg.Calibration_xml = str(cfg_dstdir / "calibration.xml")
        mcacfg.RawImage_Path = self.srcdir / common_cfg.pattern[self.seq_name]
        mcacfg.Output_Path = img_dstdir
        mcacfg.start_frame = common_cfg.start_idx[self.seq_name]
        mcacfg.end_frame = mcacfg.start_frame + self.frames - 1
        mcacfg.crop_ratio = self.crop_ratio

        mcacfg_dstpath = cfg_dstdir / "mca.cfg"
        mcacfg.to_file(mcacfg_dstpath)

        # Run command
        cmds = [
            node_cfg.app.preproc,
            mcacfg_dstpath,
        ]

        run_cmds(cmds)
