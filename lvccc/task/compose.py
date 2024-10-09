import functools
from pathlib import Path
from typing import ClassVar

from PIL import Image
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


@dataclass
class ComposeTask(NonRootTask["ComposeTask"]):
    task: ClassVar[str] = "compose"

    @functools.cached_property
    def views(self) -> int:
        return self.parent.views

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)

        refimg_path = get_any_file(self.srcdir / "frame#001")
        refimg = Image.open(refimg_path)
        width, height = refimg.size

        for view_idx in range(1, self.views * self.views + 1):
            cmds = [
                config.app.ffmpeg,
                "-i",
                self.srcdir / "frame#%03d" / f"image_{view_idx:0>3}.png",
                "-vf",
                "format=yuv420p",
                "-frames:v",
                self.frames,
                yuv_dstdir / f"{self.full_tag}-v{view_idx:0>3}-{width}x{height}.yuv",
                "-v",
                "error",
                "-y",
            ]

            run_cmds(cmds)
