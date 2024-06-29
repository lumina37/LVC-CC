import functools
import shutil
from pathlib import Path
from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..helper import mkdir, run_cmds
from .base import BaseTask


@dataclass
class CopyTask(BaseTask["CopyTask"]):
    task: str = "copy"

    DEFAULT_START_IDX: ClassVar[int] = -1
    start_idx: int = DEFAULT_START_IDX
    frames: int = 0

    def __post_init__(self) -> None:
        common_cfg = get_common_cfg()
        if self.start_idx == self.DEFAULT_START_IDX:
            self.start_idx = common_cfg.start_idx[self.seq_name]

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        node_cfg = get_node_cfg()
        srcdir = node_cfg.path.dataset / "img" / self.seq_name
        return srcdir

    def _run(self) -> None:
        common_cfg = get_common_cfg()

        fname_pattern = common_cfg.pattern[self.seq_name]
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        if fname_pattern.endswith('.png'):
            for cnt, idx in enumerate(range(self.start_idx, self.start_idx + self.frames), 1):
                src_fname = fname_pattern % idx
                dst_fname = common_cfg.default_pattern % cnt
                shutil.copy(self.srcdir / src_fname, img_dstdir / dst_fname)

        else:
            node_cfg = get_node_cfg()
            cmds = [
                node_cfg.app.ffmpeg,
                "-i",
                self.srcdir / fname_pattern,
                "-start_number",
                self.start_idx,
                "-frames:v",
                self.frames,
                img_dstdir / common_cfg.default_pattern,
                "-v",
                "warning",
                "-y",
            ]

            run_cmds(cmds)

            if self.start_idx > 1:
                rg = range(1, self.frames + 1)
            elif self.start_idx == 0:
                rg = range(self.frames, 0, -1)
            else:
                rg = []

            for i in rg:
                src_fname = common_cfg.default_pattern % (self.start_idx + i - 1)
                dst_fname = common_cfg.default_pattern % i
                (img_dstdir / src_fname).rename(img_dstdir / dst_fname)
