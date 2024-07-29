import functools
import math
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import MCACfg, get_config
from ..helper import mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dataclass
class PostprocTask(NonRootTask["PostprocTask"]):
    task: str = "postproc"

    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        # Copy `calibration.xml`
        cfg_srcdir = Path("config") / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        # Make dst dir
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        # Mod and write `mca.cfg`
        mcacfg_srcpath = cfg_srcdir / "mca.cfg"
        mcacfg = MCACfg.from_file(mcacfg_srcpath)

        calib_cfg_name = "rlc.xml" if mcacfg.pipeline == 0 else "tlct.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        mcacfg.Calibration_xml = str(cfg_dstpath)
        mcacfg.RawImage_Path = self.srcdir / config.default_pattern
        mcacfg.Output_Path = img_dstdir / config.default_pattern
        mcacfg.start_frame = 1
        mcacfg.end_frame = self.frames
        mcacfg.crop_ratio = self.crop_ratio

        mcacfg_dstpath = cfg_dstdir / "mca.cfg"
        mcacfg.to_file(mcacfg_dstpath)

        # Run command
        cmds = [
            config.app.postproc,
            mcacfg_dstpath,
        ]

        run_cmds(cmds)
