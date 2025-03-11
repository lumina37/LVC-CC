from __future__ import annotations

import dataclasses as dcs
import functools
import re
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import CalibCfg, PreprocCfg, get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dcs.dataclass
class PreprocTask(NonRootTask["PreprocTask"]):
    """
    MCA preprocess.
    """

    task: ClassVar[str] = "preproc"

    crop_size: int = 0

    @functools.cached_property
    def self_tag(self) -> str:
        return f"proc-c{self.crop_size}"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def run(self) -> None:
        # Prepare
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")

        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        preproc_cfg = PreprocCfg()
        preproc_cfg.FramesToBeEncoded = self.frames
        calib_cfg = CalibCfg.from_file(cfg_srcdir / "calib.cfg")
        preproc_cfg.SourceWidth = calib_cfg.LensletWidth
        preproc_cfg.SourceHeight = calib_cfg.LensletHeight
        codec_cfg_dstpath = cfg_dstdir / "codec.cfg"
        preproc_cfg.to_file(codec_cfg_dstpath)

        calib_cfg_dstpath = cfg_dstdir / "calib.xml"
        shutil.copyfile(cfg_srcdir / "calib.xml", calib_cfg_dstpath)

        # Run
        cmds = [
            config.app.processor,
            "-proc",
            "Pre",
            "-i",
            yuv_srcpath,
            "-o",
            ".",
            "-config",
            codec_cfg_dstpath.relative_to(self.dstdir),
            "-calib",
            calib_cfg_dstpath.relative_to(self.dstdir),
            "-patch",
            self.crop_size,
            "-log",
            "proc.log",
        ]

        run_cmds(cmds, cwd=self.dstdir)

        yuv_dstpath = get_any_file(self.dstdir, "*.yuv")
        size = re.search(r"_(\d+x\d+)_", yuv_dstpath.name).group(1)
        new_stem = f"{self.tag}-{size}"
        yuv_dstpath.rename(yuv_dstpath.with_stem(new_stem))
