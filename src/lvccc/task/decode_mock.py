from __future__ import annotations

import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

from ..helper import get_any_file, mkdir
from .base import NonRootTask
from .infomap import query


@dcs.dataclass
class DecodeMockTask(NonRootTask["DecodeMockTask"]):
    """
    Mock Decode.
    """

    task: ClassVar[str] = "decmock"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def run(self) -> None:
        mkdir(self.dstdir)

        srcpath = get_any_file(
            Path("/workspace/mpeg/mpeg/zrb/xueshi-cc/output") / self.seq_name / f"qp{self.parent.qp}" / "dec"
        )
        dstpath = self.dstdir / f"{self.tag}.yuv"
        dstpath.symlink_to(srcpath)
