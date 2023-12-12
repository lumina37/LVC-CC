import functools
from dataclasses import dataclass
from typing import ClassVar

from ..cfg.node import get_node_cfg
from ..logging import get_logger
from ..utils import get_first_file, get_src_pattern, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class Png2yuvTask(BaseTask):
    task_name: ClassVar[str] = "png2yuv"

    seq_name: str = ""
    frames: int = 30

    @functools.cached_property
    def dirname(self) -> str:
        if self.pretask:
            return f"{self.task_name}-{self.seq_name}-{self.pretask.shorthash}-{self.shorthash}"
        else:
            return f"{self.task_name}-{self.seq_name}-{self.shorthash}"

    def run(self) -> None:
        log = get_logger()
        node_cfg = get_node_cfg()

        if self.pretask:
            srcdir = query(self.pretask)
            srcdir = srcdir / "img"
        else:
            srcdir = node_cfg.path.dataset / "img" / self.seq_name

        fname_pattern = get_src_pattern(get_first_file(srcdir).name)

        mkdir(self.dstdir)

        cmds = [
            node_cfg.app.ffmpeg,
            "-i",
            srcdir / fname_pattern,
            "-vf",
            "format=yuv420p",
            "-vframes",
            self.frames,
            self.dstdir / "out.yuv",
            "-v",
            "warning",
            "-y",
        ]
        log.info(cmds)

        run_cmds(cmds)

        self.dump_metainfo()
