import functools
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import TLCTCfg
from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class TLCTRenderTask(BaseTask):
    task: str = "tlct"

    frames: int = 30
    views: int = 5

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        # Mod and write `rlc.cfg`
        tlctcfg_srcpath = cfg_srcdir / "tlct.cfg"
        tlctcfg = TLCTCfg.from_file(tlctcfg_srcpath)

        calib_cfg_name = "tlct.xml"
        shutil.copy(cfg_srcdir / calib_cfg_name, cfg_dstdir)
        tlctcfg.pipeline = 1
        tlctcfg.Calibration_xml = str(cfg_dstdir / calib_cfg_name)
        tlctcfg.RawImage_Path = str(self.srcdir / common_cfg.default_pattern)
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        tlctcfg.Output_Path = str(img_dstdir / common_cfg.default_pattern.rstrip('.png'))
        tlctcfg.viewNum = self.views
        # Render frames with id \in [start, end]
        tlctcfg.start_frame = 1
        tlctcfg.end_frame = self.frames

        tlctcfg_dstpath = cfg_dstdir / "tlct.cfg"
        tlctcfg.to_file(tlctcfg_dstpath)

        # Prepare and run command
        cmds = [
            node_cfg.app.rlc,
            tlctcfg_dstpath,
        ]

        run_cmds(cmds)
