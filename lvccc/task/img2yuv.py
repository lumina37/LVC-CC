import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

from PIL import Image

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .copy import ImgCopyTask
from .infomap import query


@dcs.dataclass
class Img2yuvTask(NonRootTask["Img2yuvTask"]):
    task: ClassVar[str] = "img2yuv"

    @functools.cached_property
    def tag(self) -> str:
        return "anchor" if isinstance(self.parent, ImgCopyTask) else ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()
        mkdir(self.dstdir)

        refimg_path = get_any_file(self.srcdir)
        refimg = Image.open(refimg_path)
        width, height = refimg.size

        cmds = [
            config.app.ffmpeg,
            "-i",
            self.srcdir / config.default_pattern,
            "-vf",
            "format=yuv420p",
            "-frames:v",
            self.frames,
            f"{self.full_tag}-{width}x{height}.yuv",
            "-v",
            "error",
            "-y",
        ]

        run_cmds(cmds, cwd=self.dstdir)
