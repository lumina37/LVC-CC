from __future__ import annotations

import dataclasses as dcs
import functools
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, ClassVar

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .infomap import query
from .preproc import PreprocTask

if TYPE_CHECKING:
    from pathlib import Path


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

    def run(self) -> None:
        # Prepare
        config = get_config()

        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")

        for idx, task_dict in enumerate(self.chain):
            if task_dict["task"] == PreprocTask.task:
                preproc_task = self.ancestor(idx)

        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        proc_log_srcpath = preproc_task.dstdir / "proc.log"
        preproc_log_dstpath = cfg_dstdir / "proc.log"
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

        run_cmds(cmds, output=subprocess.DEVNULL, cwd=self.dstdir)

        yuv_dstpath = get_any_file(self.dstdir, "*.yuv")
        size = re.search(r"_(\d+x\d+)_", yuv_dstpath.name).group(1)
        new_stem = f"{self.tag}-{size}"
        yuv_dstpath.rename(yuv_dstpath.with_stem(new_stem))
