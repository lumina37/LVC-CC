import functools
import shutil
from pathlib import Path
from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..config import RLCCfg, get_config
from ..helper import mkdir, run_cmds
from .base import RootTask


@dataclass
class ImgCopyTask(RootTask["ImgCopyTask"]):
    task: str = "imgcopy"

    DEFAULT_START_IDX: ClassVar[int] = -1

    seq_name: str = ""
    frames: int = 0
    start_idx: int = DEFAULT_START_IDX

    def __post_init__(self) -> None:
        common_cfg = get_config()
        if self.start_idx == self.DEFAULT_START_IDX:
            self.start_idx = common_cfg.start_idx[self.seq_name]

    @functools.cached_property
    def tag(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _run(self) -> None:
        config = get_config()

        input_dir = config.path.input
        input_pattern = config.path.pattern[self.seq_name]
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        if input_pattern.endswith('.png'):
            for cnt, idx in enumerate(range(self.start_idx, self.start_idx + self.frames), 1):
                src_fpath = input_dir / (input_pattern % idx)
                dst_fname = config.default_pattern % cnt
                shutil.copyfile(src_fpath, img_dstdir / dst_fname)

        else:
            cmds = [
                config.app.ffmpeg,
                "-i",
                input_dir / input_pattern,
                "-start_number",
                self.start_idx,
                "-frames:v",
                self.frames,
                img_dstdir / config.default_pattern,
                "-v",
                "warning",
                "-y",
            ]

            run_cmds(cmds)

            if self.start_idx > 1:
                rg = range(1, self.frames + 1)
            elif self.start_idx == 0:
                rg = range(self.frames, 0, -1)
            else:
                rg = []

            for i in rg:
                src_fname = config.default_pattern % (self.start_idx + i - 1)
                dst_fname = config.default_pattern % i
                (img_dstdir / src_fname).rename(img_dstdir / dst_fname)


@dataclass
class YuvCopyTask(RootTask["YuvCopyTask"]):
    task: str = "yuvcopy"

    DEFAULT_START_IDX: ClassVar[int] = 0

    seq_name: str = ""
    frames: int = 0
    start_idx: int = DEFAULT_START_IDX

    @functools.cached_property
    def tag(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _run(self) -> None:
        config = get_config()

        input_dir = config.path.input
        srcyuv_path = next(input_dir.glob('*.yuv'))
        mkdir(self.dstdir)

        cfg_srcdir = Path("config") / self.seq_name
        rlccfg_srcpath = cfg_srcdir / "rlc.cfg"
        rlccfg = RLCCfg.from_file(rlccfg_srcpath)

        width = rlccfg.width
        height = rlccfg.height
        yuvsize = srcyuv_path.stat().st_size
        actual_frames = int(yuvsize / (width * height / 2 * 3))
        dst_fname = f"{self.full_tag}-{width}x{height}.yuv"
        dstyuv_path = self.dstdir / dst_fname

        if self.start_idx == 0 and actual_frames == self.frames:
            shutil.copyfile(srcyuv_path, dstyuv_path)

        elif (self.frames + self.start_idx) < actual_frames:
            cmds = [
                config.app.ffmpeg,
                "-s",
                f"{width}x{height}",
                "-pix_fmt",
                "yuv420p",
                "-i",
                srcyuv_path,
                "-vf",
                f"select='between(n\\,{self.start_idx}\\,{self.start_idx+self.frames-1})'",
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                "yuv420p",
                dstyuv_path,
                "-v",
                "warning",
                "-y",
            ]

            run_cmds(cmds)

        else:
            raise ValueError(f"start_idx+frames>actual_frames: {self.start_idx+self.frames}>{actual_frames}")
