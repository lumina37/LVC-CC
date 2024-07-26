import dataclasses as dcs
import functools
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dataclass
class ComposeTask(NonRootTask["ComposeTask"]):
    task: str = "compose"

    views: int = 5

    @functools.cached_property
    def tag(self) -> str:
        return ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)

        for view_idx in range(1, self.views * self.views + 1):
            cmds = [
                config.app.ffmpeg,
                "-i",
                self.srcdir / "frame#%03d" / f"image_{view_idx:0>3}.png",
                "-vf",
                "format=yuv420p",
                "-frames:v",
                self.frames,
                yuv_dstdir / f"{view_idx}.yuv",
                "-v",
                "warning",
                "-y",
            ]

            run_cmds(cmds)
