import functools

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from ..logging import get_logger
from ..utils import get_first_file, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class Yuv2pngTask(BaseTask):
    task: str = "yuv2png"

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.pretask.shorthash}-{self.shorthash}"

    def run(self) -> None:
        log = get_logger()
        node_cfg = get_node_cfg()

        assert self.pretask is not None

        refimg_path = get_first_file(self.pretask.pretask.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        srcdir = query(self.pretask)
        srcpath = srcdir / "out.yuv"

        dstdir = self.dstdir / "img"
        mkdir(dstdir)

        cmds = [
            node_cfg.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-i",
            srcpath,
            "-vf",
            "format=yuv444p",
            dstdir / "frame#%03d.png",
            "-v",
            "warning",
        ]

        run_cmds(cmds)
        log.info(f"Completed! cmds={cmds}")

        self.dump_metainfo()
