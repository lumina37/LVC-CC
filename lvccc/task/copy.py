import functools
import shutil
from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..config import get_config
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .const import DEFAULT_PATTERN


@dataclass
class CopyTask(BaseTask["CopyTask"]):
    task: str = "copy"

    DEFAULT_START_IDX: ClassVar[int] = -1

    start_idx: int = DEFAULT_START_IDX
    frames: int = 0

    def __post_init__(self) -> None:
        common_cfg = get_config()
        if self.start_idx == self.DEFAULT_START_IDX:
            self.start_idx = common_cfg.start_idx[self.seq_name]

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _run(self) -> None:
        config = get_config()

        input_dir = config.path.input
        input_pattern = config.path.pattern[self.seq_name]
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        if input_pattern.endswith('.png'):
            for cnt, idx in enumerate(range(self.start_idx, self.start_idx + self.frames), 1):
                src_fpath = input_dir / (input_pattern % idx)
                dst_fname = DEFAULT_PATTERN % cnt
                shutil.copyfile(src_fpath, img_dstdir / dst_fname)

        else:
            cmds = [
                config.app.ffmpeg,
                "-i",
                input_dir / input_pattern,
                "-start_number",
                self.start_idx,
                "-frames:v",
                self.frames,
                img_dstdir / DEFAULT_PATTERN,
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
                src_fname = DEFAULT_PATTERN % (self.start_idx + i - 1)
                dst_fname = DEFAULT_PATTERN % i
                (img_dstdir / src_fname).rename(img_dstdir / dst_fname)