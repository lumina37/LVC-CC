import functools
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class ComposeTask(BaseTask["ComposeTask"]):
    task: str = "compose"

    frames: int = 0
    views: int = 5

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()

        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)

        for view_idx in range(1, self.views * self.views + 1):
            cmds = [
                node_cfg.app.ffmpeg,
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
