import dataclasses as dcs
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import MCACfg, get_config
from ..helper import detect_pattern, get_any_file, get_first_file, mkdir, run_cmds
from .base import RootTask


@dcs.dataclass
class ImgCopyTask(RootTask["ImgCopyTask"]):
    task: ClassVar[str] = "imgcopy"

    seq_name: str = ""
    frames: int = 1
    start_idx: int = 0

    @functools.cached_property
    def self_tag(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _inner_run(self) -> None:
        config = get_config()

        input_dir = config.path.input / self.seq_name
        first_imgpath = get_first_file(input_dir)
        input_pattern, start_idx = detect_pattern(first_imgpath.name)
        start_idx += self.start_idx
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        if input_pattern.endswith('.png'):
            for cnt, idx in enumerate(range(start_idx, start_idx + self.frames), 1):
                src_fpath = input_dir / (input_pattern % idx)
                dst_fname = config.default_pattern % cnt
                shutil.copyfile(src_fpath, img_dstdir / dst_fname)

        else:
            cmds = [
                config.app.ffmpeg,
                "-i",
                input_dir / input_pattern,
                "-start_number",
                start_idx,
                "-frames:v",
                self.frames,
                img_dstdir / config.default_pattern,
                "-v",
                "error",
                "-y",
            ]

            run_cmds(cmds)

            if start_idx > 1:
                rg = range(1, self.frames + 1)
            elif start_idx == 0:
                rg = range(self.frames, 0, -1)
            else:
                rg = []

            for i in rg:
                src_fname = config.default_pattern % (start_idx + i - 1)
                dst_fname = config.default_pattern % i
                (img_dstdir / src_fname).rename(img_dstdir / dst_fname)


@dcs.dataclass
class YuvCopyTask(RootTask["YuvCopyTask"]):
    task: ClassVar[str] = "yuvcopy"

    seq_name: str = ""
    frames: int = 1
    start_idx: int = 0

    @functools.cached_property
    def self_tag(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _inner_run(self) -> None:
        config = get_config()

        input_dir = config.path.input
        srcdir = input_dir / self.seq_name
        srcpath = get_any_file(srcdir, '*.yuv')
        mkdir(self.dstdir)

        cfg_srcdir = Path("config") / self.seq_name
        mcacfg_srcpath = cfg_srcdir / "mca.cfg"
        mcacfg = MCACfg.from_file(mcacfg_srcpath)

        width = mcacfg.width
        height = mcacfg.height
        yuvsize = srcpath.stat().st_size
        actual_frames = int(yuvsize / (width * height / 2 * 3))
        dst_fname = f"{self.tag}-{width}x{height}.yuv"
        dstpath = self.dstdir / dst_fname

        if self.start_idx == 0 and actual_frames == self.frames:
            shutil.copyfile(srcpath, dstpath)

        elif (self.frames + self.start_idx) < actual_frames:
            cmds = [
                config.app.ffmpeg,
                "-s",
                f"{width}x{height}",
                "-pix_fmt",
                "yuv420p",
                "-i",
                srcpath,
                "-vf",
                f"select='between(n\\,{self.start_idx}\\,{self.start_idx+self.frames-1})'",
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                "yuv420p",
                dstpath,
                "-v",
                "error",
                "-y",
            ]

            run_cmds(cmds)

        else:
            raise ValueError(f"start_idx+frames>actual_frames: {self.start_idx+self.frames}>{actual_frames}")
