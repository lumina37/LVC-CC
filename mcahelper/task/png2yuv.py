import functools
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..helper import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class Png2yuvTask(BaseTask["Png2yuvTask"]):
    task: str = "png2yuv"

    frames: int = 0

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()
        mkdir(self.dstdir)

        cmds = [
            node_cfg.app.ffmpeg,
            "-i",
            self.srcdir / common_cfg.default_pattern,
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
