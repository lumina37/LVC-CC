import functools
from pathlib import Path

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import get_first_file, mkdir, run_cmds
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


@dataclass
class Png2yuvTask(NonRootTask["Png2yuvTask"]):
    task: str = "png2yuv"

    @functools.cached_property
    def tag(self) -> str:
        return "anchor" if isinstance(self.parent, CopyTask) else ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()
        mkdir(self.dstdir)

        refimg_path = get_first_file(self.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        cmds = [
            config.app.ffmpeg,
            "-i",
            self.srcdir / config.default_pattern,
            "-vf",
            "format=yuv420p",
            "-frames:v",
            self.frames,
            self.dstdir / f"{self.full_tag}-{width}x{height}.yuv",
            "-v",
            "warning",
            "-y",
        ]

        run_cmds(cmds)
