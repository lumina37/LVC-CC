from __future__ import annotations

import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

from ..helper import get_any_file, mkdir
from .base import NonRootTask
from .copy import CopyTask


@dcs.dataclass
class EncodeMockTask(NonRootTask["EncodeMockTask"]):
    """
    Mock Encode.
    """

    task: ClassVar[str] = "encmock"
    vtm_ra_cfg_path: ClassVar[Path] = Path("config") / "vtmRA.cfg"

    qp: int = 0

    @functools.cached_property
    def self_tag(self) -> str:
        tag = f"QP{self.qp}"
        if isinstance(self.parent, CopyTask):
            return "anchor-" + tag
        return tag

    def run(self) -> None:
        mkdir(self.dstdir)

        srcpath = get_any_file(
            Path("/workspace/mpeg/mpeg/zrb/xueshi-cc/output") / self.seq_name / f"qp{self.qp}" / "enc", "*.bin"
        )
        dstpath = self.dstdir / f"{self.tag}.bin"
        dstpath.symlink_to(srcpath)
