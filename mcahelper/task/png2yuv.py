import functools
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from ..utils import get_first_file, get_src_pattern, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class Png2yuvTask(BaseTask):
    task: str = "png2yuv"

    frames: int = 30

    @functools.cached_property
    def dirname(self) -> str:
        if self.parent:
            return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"
        else:
            return f"{self.task}-{self.seq_name}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        if self.parent:
            srcdir = query(self.parent) / "img"
        else:
            node_cfg = get_node_cfg()
            srcdir = node_cfg.path.dataset / "img" / self.seq_name
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()

        fname_pattern = get_src_pattern(get_first_file(self.srcdir).name)

        mkdir(self.dstdir)

        cmds = [
            node_cfg.app.ffmpeg,
            "-i",
            self.srcdir / fname_pattern,
            "-vf",
            "format=yuv420p",
            "-vframes",
            self.frames,
            self.dstdir / "out.yuv",
            "-v",
            "warning",
            "-y",
        ]

        run_cmds(cmds)
