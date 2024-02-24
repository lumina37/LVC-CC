import functools
import math
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..cfg import RaytrixCfg
from ..cfg.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class PostprocTask(BaseTask):
    task: str = "postproc"

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

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        shutil.copy(cfg_srcdir / "calibration.xml", cfg_dstdir)

        # Mod and write `rlc.cfg`
        rlccfg_srcpath = cfg_srcdir / "rlc.cfg"
        rlccfg = RaytrixCfg.from_file(rlccfg_srcpath)

        rlccfg.Calibration_xml = str(cfg_dstdir / "calibration.xml")
        rlccfg.crop_ratio = self.crop_ratio

        rlccfg_dstpath = cfg_dstdir / "rlc.cfg"
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        cmds = [
            node_cfg.app.postproc,
            rlccfg_dstpath,
            self.srcdir,
            img_dstdir,
        ]

        run_cmds(cmds)
