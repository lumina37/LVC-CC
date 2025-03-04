from __future__ import annotations

import dataclasses as dcs
import functools
import math
import re
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, run_cmds
from .base import NonRootTask
from .infomap import query
from .preproc import PreprocTask


@dcs.dataclass
class PostprocTask(NonRootTask["PostprocTask"]):
    """
    MCA postprocess.
    """

    task: ClassVar[str] = "postproc"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _inner_run(self) -> None:
        # Prepare
        config = get_config()

        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")

        for task in self.chain:
            if isinstance(task, PreprocTask):
                preproc_task = task
        proc_log_srcpath = preproc_task.dstdir / "proc.log"
        preproc_log_dstpath = self.dstdir / "proc.log"
        shutil.copyfile(proc_log_srcpath, preproc_log_dstpath)

        # Run
        cmds = [
            config.app.processor,
            "-proc",
            "Post",
            "-i",
            yuv_srcpath,
            "-o",
            ".",
            "-log",
            preproc_log_dstpath.relative_to(self.dstdir),
        ]

        run_cmds(cmds, cwd=self.dstdir)

        yuv_dstpath = get_any_file(self.dstdir, "*.yuv")
        size = re.search(r"_(\d+x\d+)_", yuv_dstpath.name).group(1)
        new_stem = f"{self.tag}-{size}"
        yuv_dstpath.rename(yuv_dstpath.with_stem(new_stem))
