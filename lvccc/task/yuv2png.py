import functools

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import get_first_file, mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dataclass
class Yuv2pngTask(NonRootTask["Yuv2pngTask"]):
    task: str = "yuv2png"

    @functools.cached_property
    def tag(self) -> str:
        return ""

    def _run(self) -> None:
        config = get_config()

        refimg_path = get_first_file(self.parent.parent.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        srcdir = query(self.parent)
        srcpath = next(srcdir.glob('*.yuv'))

        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        cmds = [
            config.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-i",
            srcpath,
            "-vf",
            "format=yuv444p",
            "-frames:v",
            self.frames,
            img_dstdir / config.default_pattern,
            "-v",
            "warning",
        ]

        run_cmds(cmds)
