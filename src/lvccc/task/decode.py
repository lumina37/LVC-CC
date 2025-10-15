from __future__ import annotations

import dataclasses as dcs
import functools
from typing import TYPE_CHECKING, ClassVar

from ..config import get_config
from ..helper import get_any_file, run_cmds
from .base import NonRootTask
from .infomap import query

if TYPE_CHECKING:
    from pathlib import Path


@dcs.dataclass
class DecodeTask(NonRootTask["DecodeTask"]):
    """
    VVC Decode (with VTM-11.0).
    """

    task: ClassVar[str] = "decode"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def run(self) -> None:
        # Prepare
        config = get_config()

        srcpath = get_any_file(self.srcdir, "*.bin")

        dstpath_pattern = self.dstdir / self.tag
        log_path = dstpath_pattern.with_suffix(".log")

        # Run
        with log_path.open("w", encoding="utf-8") as logf:
            cmds = [
                config.app.decoder,
                "--OutputBitDepth=8",
                "-b",
                srcpath,
                "-o",
                f"{self.tag}.yuv",
            ]

            run_cmds(cmds, output=logf, cwd=self.dstdir)
