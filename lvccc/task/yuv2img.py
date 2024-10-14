import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import mkdir, run_cmds, size_from_filename
from .base import NonRootTask
from .infomap import query


@dcs.dataclass
class Yuv2imgTask(NonRootTask["Yuv2imgTask"]):
    task: ClassVar[str] = "yuv2img"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _run(self) -> None:
        config = get_config()

        srcpath = next(self.srcdir.glob('*.yuv'))

        width, height = size_from_filename(srcpath.name)

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
            "error",
        ]

        run_cmds(cmds)
