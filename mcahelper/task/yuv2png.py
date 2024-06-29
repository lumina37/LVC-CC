import functools

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..utils import get_first_file, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class Yuv2pngTask(BaseTask["Yuv2pngTask"]):
    task: str = "yuv2png"

    frames: int = 0

    @functools.cached_property
    def dirname(self) -> str:
        assert self.parent is not None
        return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()

        refimg_path = get_first_file(self.parent.parent.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        srcdir = query(self.parent)
        srcpath = srcdir / "out.yuv"

        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        cmds = [
            node_cfg.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-i",
            srcpath,
            "-vf",
            "format=yuv444p",
            "-frames:v",
            self.frames,
            img_dstdir / common_cfg.default_pattern,
            "-v",
            "warning",
        ]

        run_cmds(cmds)
