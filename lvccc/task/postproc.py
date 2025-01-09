import dataclasses as dcs
import functools
import math
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, run_cmds
from .base import NonRootTask
from .infomap import query


@dcs.dataclass
class PostprocTask(NonRootTask["PostprocTask"]):
    task: ClassVar[str] = "postproc"

    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _inner_run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")

        calib_cfg_name = "calib.cfg"
        calib_cfg_dstpath = self.dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, calib_cfg_dstpath)

        cmds = [
            config.app.proccessor,
            calib_cfg_dstpath,
            "--post",
            "-i",
            yuv_srcpath,
            "-o",
            self.dstdir,
            "--end",
            self.frames,
            "--cropRatio",
            self.crop_ratio,
        ]

        run_cmds(cmds)

        yuv_dstpath = get_any_file(self.dstdir, "*.yuv")
        _, size = yuv_dstpath.name.rsplit("-", 1)
        new_fname = f"{self.tag}-{size}"
        yuv_dstpath.rename(yuv_dstpath.with_name(new_fname))
