import functools
import shutil
from pathlib import Path

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import get_first_file, mkdir, rm, run_cmds
from .abc import TSelfTask, TVarTask
from .base import NonRootTask
from .infomap import query


@dataclass
class ComposeTask(NonRootTask["ComposeTask"]):
    task: str = "compose"

    frames_per_view: int = 0

    def with_parent(self, parent: TVarTask) -> TSelfTask:
        super().with_parent(parent)

        if self.frames_per_view <= 0:
            self.frames_per_view = int(self.frames / (self.views**2))

        return self

    @functools.cached_property
    def views(self) -> int:
        return self.parent.views

    @functools.cached_property
    def tag(self) -> str:
        return ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        tmp_dstdir = self.dstdir / "tmp"
        mkdir(tmp_dstdir)

        frame_count = 1
        for view_idx in range(1, self.views**2 + 1):
            fiew_fname = f"image_{view_idx:0>3}.png"

            for _ in range(self.frames_per_view):
                shutil.copyfile(
                    self.srcdir / f"frame#{frame_count:0>3}" / fiew_fname, tmp_dstdir / f"frame#{frame_count:0>3}.png"
                )
                frame_count += 1
                if frame_count > self.frames:
                    frame_count -= self.frames

        refimg_path = get_first_file(self.srcdir / "frame#001")
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        cmds = [
            config.app.ffmpeg,
            "-i",
            tmp_dstdir / config.default_pattern,
            "-vf",
            "format=yuv420p",
            "-frames:v",
            self.frames,
            self.dstdir / f"{self.full_tag}-{width}x{height}.yuv",
            "-v",
            "warning",
            "-y",
        ]

        run_cmds(cmds, cwd=tmp_dstdir)

        rm(tmp_dstdir)
