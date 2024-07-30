from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import mkdir, run_cmds, size_from_filename
from .base import NonRootTask
from .infomap import query


@dataclass
class Yuv2pngTask(NonRootTask["Yuv2pngTask"]):
    task: str = "yuv2png"

    def _run(self) -> None:
        config = get_config()

        srcdir = query(self.parent)
        srcpath = next(srcdir.glob('*.yuv'))

        width, height = size_from_filename(srcpath.name)

        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        cmds = [
            config.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-i",
            srcpath,
            "-vf",
            "format=yuv444p",
            "-frames:v",
            self.frames,
            img_dstdir / config.default_pattern,
            "-v",
            "warning",
        ]

        run_cmds(cmds)
