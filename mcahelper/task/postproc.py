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
from .infomap import query


@dataclass
class PostprocTask(BaseTask):
    task: str = "postproc"

    frames: int = 30
    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def dirname(self) -> str:
        assert self.parent is not None
        return f"{self.task}-{self.seq_name}-{self.crop_ratio:.3f}-{self.parent.shorthash}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        assert self.parent is not None
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()

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
        mcacfg.RawImage_Path = self.srcdir / common_cfg.default_pattern.c
        mcacfg.Output_Path = img_dstdir
        mcacfg.end_frame = self.frames - 1
        mcacfg.crop_ratio = self.crop_ratio

        mcacfg_dstpath = cfg_dstdir / "mca.cfg"
        mcacfg.to_file(mcacfg_dstpath)

        # Run command
        cmds = [
            node_cfg.app.postproc,
            mcacfg_dstpath,
        ]

        run_cmds(cmds)
