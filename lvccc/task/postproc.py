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
        # Prepare
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")

        calib_cfg_dstpath = self.dstdir / "calib.cfg"
        shutil.copyfile(cfg_srcdir / "calib.cfg", calib_cfg_dstpath)

        # Run
        cmds = [
            config.app.processor,
            calib_cfg_dstpath.relative_to(self.dstdir),
            "--post",
            "-i",
            yuv_srcpath,
            "-o",
            ".",
            "--end",
            self.frames,
            "--cropRatio",
            self.crop_ratio,
        ]

        run_cmds(cmds, cwd=self.dstdir)

        yuv_dstpath = get_any_file(self.dstdir, "*.yuv")
        _, size = yuv_dstpath.name.rsplit("-", 1)
        new_fname = f"{self.tag}-{size}"
        yuv_dstpath.rename(yuv_dstpath.with_name(new_fname))
