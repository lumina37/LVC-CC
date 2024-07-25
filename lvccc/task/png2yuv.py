import functools
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import mkdir, run_cmds
from .base import BaseTask
from .copy import CopyTask
from .infomap import query


@dataclass
class Png2yuvTask(BaseTask["Png2yuvTask"]):
    task: str = "png2yuv"

    frames: int = 0

    @functools.cached_property
    def dirname(self) -> str:
        return "anchor" if isinstance(self.parent, CopyTask) else ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()
        mkdir(self.dstdir)

        cmds = [
            config.app.ffmpeg,
            "-i",
            self.srcdir / config.default_pattern,
            "-vf",
            "format=yuv420p",
            "-frames:v",
            self.frames,
            self.dstdir / "out.yuv",
            "-v",
            "warning",
            "-y",
        ]

        run_cmds(cmds)
