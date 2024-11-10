import dataclasses as dcs
import functools
import math
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import MCACfg, get_config
from ..helper import mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dcs.dataclass
class PreprocTask(NonRootTask["PreprocTask"]):
    task: ClassVar[str] = "preproc"

    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def tag(self) -> str:
        return "mca"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        mcacfg_srcpath = cfg_srcdir / "mca.cfg"
        mcacfg = MCACfg.from_file(mcacfg_srcpath)

        calib_cfg_name = "calib.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        mcacfg.calibFile = str(cfg_dstpath)
        mcacfg.inYuv = self.srcdir / config.default_pattern
        mcacfg.outDir = img_dstdir / config.default_pattern
        mcacfg.frameBegin = 1
        mcacfg.frameEnd = self.frames
        mcacfg.crop_ratio = self.crop_ratio

        mcacfg_dstpath = cfg_dstdir / "mca.cfg"
        mcacfg.to_file(mcacfg_dstpath)

        cmds = [
            config.app.preproc,
            mcacfg_dstpath,
        ]

        run_cmds(cmds)
