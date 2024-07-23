import functools

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config.self import get_config
from ..utils import get_first_file, mkdir, run_cmds
from .base import BaseTask
from .const import DEFAULT_PATTERN
from .infomap import query


@dataclass
class Yuv2pngTask(BaseTask["Yuv2pngTask"]):
    task: str = "yuv2png"

    frames: int = 0

    @functools.cached_property
    def dirname(self) -> str:
        return ""

    def _run(self) -> None:
        config = get_config()

        refimg_path = get_first_file(self.parent.parent.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        srcdir = query(self.parent)
        srcpath = srcdir / "out.yuv"

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
            img_dstdir / DEFAULT_PATTERN,
            "-v",
            "warning",
        ]

        run_cmds(cmds)