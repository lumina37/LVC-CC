import functools
import shutil
from pathlib import Path
from typing import ClassVar

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..logging import get_logger
from ..utils import mkdir
from .base import BaseTask


@dataclass
class CopyTask(BaseTask):
    task: str = "copy"

    DEFAULT_START_IDX: ClassVar[int] = -1
    start_idx: int = DEFAULT_START_IDX
    frames: int = 30

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

            def handler(src_fname: str, cnt: int):
                dst_fname = common_cfg.default_pattern.py.format(cnt)
                shutil.copy(self.srcdir / src_fname, img_dstdir / dst_fname)

        else:

            def handler(src_fname: str, cnt: int):
                img = cv.imread(str(self.srcdir / src_fname))
                dst_fname = common_cfg.default_pattern.py.format(cnt)
                cv.imwrite(str(img_dstdir / dst_fname), img)

        for cnt, idx in enumerate(range(self.start_idx, self.start_idx + self.frames), 1):
            src_fname = fname_pattern.format(idx)
            handler(src_fname, cnt)

        log = get_logger()
        log.info("Completed!")
