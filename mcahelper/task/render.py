import functools
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import RLCCfg
from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class RenderTask(BaseTask):
    task: str = "render"

    frames: int = 30
    views: int = 5

    @functools.cached_property
    def dirname(self) -> str:
        if self.parent:
            return f"{self.task}-{self.seq_name}-{self.views}-{self.parent.shorthash}-{self.shorthash}"
        else:
            return f"{self.task}-{self.seq_name}-{self.views}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        if self.parent:
            srcdir = query(self.parent) / "img"
        else:
            node_cfg = get_node_cfg()
            srcdir = node_cfg.path.dataset / "img" / self.seq_name
        return srcdir

    @functools.cached_property
    def srcpattern(self) -> Path:
        if self.parent:
            srcpattern = self.srcdir / "frame#%03d.png"
        else:
            common_cfg = get_common_cfg()
            srcpattern = self.srcdir / common_cfg.pattern[self.seq_name]
        return srcpattern

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        shutil.copy(cfg_srcdir / "calibration.xml", cfg_dstdir)

        # Mod and write `rlc.cfg`
        rlccfg_srcpath = cfg_srcdir / "rlc.cfg"
        rlccfg = RLCCfg.from_file(rlccfg_srcpath)

        rlccfg.Calibration_xml = str(cfg_dstdir / "calibration.xml")
        rlccfg.RawImage_Path = str(self.srcpattern)
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        rlccfg.Output_Path = str(img_dstdir / "frame#%03d")
        rlccfg.Isfiltering = 1
        rlccfg.viewNum = self.views
        # Render frames with id \in [start, end]
        rlccfg.start_frame = common_cfg.start_idx[self.seq_name]
        rlccfg.end_frame = rlccfg.start_frame + self.frames - 1

        rlccfg_dstpath = cfg_dstdir / "rlc.cfg"
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command
        cmds = [
            node_cfg.app.rlc,
            rlccfg_dstpath,
        ]

        tmpwd = self.dstdir / "tmpwd"
        mkdir(tmpwd)

        run_cmds(cmds, cwd=tmpwd)
