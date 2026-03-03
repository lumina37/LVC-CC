from __future__ import annotations

import dataclasses as dcs
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


@dcs.dataclass
class ConvertTask(NonRootTask["ConvertTask"]):
    """
    Multi-view conversion (with TLCT).
    """

    task: ClassVar[str] = "convert"

    views: int = 1

    @functools.cached_property
    def self_tag(self) -> str:
        if isinstance(self.parent, CopyTask):
            return "base"
        return ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    @functools.cached_property
    def calib_cfg_path(self) -> Path:
        return Path("config") / self.seq_name / "tlct" / "calib.cfg"

    @functools.cached_property
    def extra_args(self) -> list[str]:
        extra_args_path = Path("config") / self.seq_name / "tlct" / "convert.sh"
        with extra_args_path.open() as f:
            extra_args = f.read().split(" ")
            return extra_args

    def run(self) -> None:
        # Prepare
        config = get_config()

        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        calib_cfg_dstpath = cfg_dstdir / "calib.cfg"
        shutil.copyfile(self.calib_cfg_path, calib_cfg_dstpath)

        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")
        yuv_reldir = "yuv"
        yuv_dstdir = self.dstdir / yuv_reldir
        mkdir(yuv_dstdir)

        # Run
        cmds = [
            config.app.convertor.TLCT,
            calib_cfg_dstpath.relative_to(self.dstdir),
            "-i",
            yuv_srcpath,
            "-o",
            yuv_reldir,
            "--end",
            self.frames,
            "--views",
            self.views,
            *self.extra_args,
        ]

        run_cmds(cmds, cwd=self.dstdir)

        for yuv_path in list(yuv_dstdir.iterdir()):
            new_fname = f"{self.tag}-{yuv_path.name}"
            yuv_path.rename(yuv_path.with_name(new_fname))
