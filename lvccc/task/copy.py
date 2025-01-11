import dataclasses as dcs
import functools
import hashlib
import shutil
from pathlib import Path
from typing import ClassVar

import yuvio

from ..config import CalibCfg, get_config
from ..helper import get_any_file, mkdir
from ..logging import get_logger
from .base import RootTask


@dcs.dataclass
class CopyTask(RootTask["CopyTask"]):
    task: ClassVar[str] = "copy"

    seq_name: str = ""
    frames: int = 1
    start_idx: int = 0

    @functools.cached_property
    def self_tag(self) -> str:
        return f"{self.seq_name}-f{self.frames}"

    def _inner_run(self) -> None:
        config = get_config()

        input_dir = config.dir.input
        srcdir = input_dir / self.seq_name
        srcpath = get_any_file(srcdir, "*.yuv")

        if self.seq_name not in config.md5:
            logger = get_logger()
            logger.warning(f"MD5 checksum of {self.seq_name} is not set")

        md5_state = hashlib.md5(usedforsecurity=False)
        with srcpath.open("rb") as yuvf:
            while chunk := yuvf.read(4 * 1024):
                md5_state.update(chunk)
        md5_hex = md5_state.hexdigest()
        if md5_hex != config.md5[self.seq_name]:
            logger = get_logger()
            logger.warning(f"MD5 checksum does not match for {srcpath}")

        mkdir(self.dstdir)

        cfg_srcdir = Path("config") / self.seq_name
        with (cfg_srcdir / "calib.cfg").open(encoding="utf-8") as f:
            calib_cfg = CalibCfg.load(f)

        width = calib_cfg.LensletWidth
        height = calib_cfg.LensletHeight
        yuvsize = srcpath.stat().st_size
        framesize = width * height // 2 * 3
        actual_frames = yuvsize // framesize
        dst_fname = f"{self.tag}-{width}x{height}.yuv"
        dstpath = self.dstdir / dst_fname

        if self.start_idx == 0 and actual_frames == self.frames:
            shutil.copyfile(srcpath, dstpath)

        elif (self.frames + self.start_idx) < actual_frames:
            reader = yuvio.get_reader(srcpath, width, height, "yuv420p")
            writer = yuvio.get_writer(dstpath, width, height, "yuv420p")
            for idx in range(self.start_idx, self.frames + self.start_idx):
                yuv_frame = reader.read(idx, 1)
                writer.write(yuv_frame)

        else:
            raise ValueError(f"start_idx+frames>actual_frames: {self.start_idx + self.frames}>{actual_frames}")
