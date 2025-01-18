from __future__ import annotations

import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

import yuvio

from ..config import CalibCfg, get_config
from ..helper import SHA1Cache, compute_sha1, get_any_file, get_sha1, mtime
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
        # Check SHA1
        config = get_config()

        srcdir = config.dir.input / self.seq_name
        srcpath = get_any_file(srcdir, "*.yuv")

        cfg_srcdir = Path("config") / self.seq_name
        sha1_path = cfg_srcdir / "checksum.sha1"
        except_sha1 = get_sha1(sha1_path)
        sha1_cache = SHA1Cache()
        cached_mtime = sha1_cache[except_sha1]
        if (yuv_mtime := mtime(srcpath)) > cached_mtime:
            sha1 = compute_sha1(srcpath)
            if sha1 != except_sha1:
                logger = get_logger()
                logger.warning(f"sha1 checksum does not match for {srcpath}")
            else:
                sha1_cache[sha1] = yuv_mtime

        # Prepare
        calib_cfg = CalibCfg.from_file(cfg_srcdir / "calib.cfg")
        width = calib_cfg.LensletWidth
        height = calib_cfg.LensletHeight
        framesize = width * height // 2 * 3
        yuvsize = srcpath.stat().st_size
        if yuvsize % framesize:
            raise ValueError(f"yuvsize%framesize!=0: {yuvsize}%{framesize}!=0 for {srcpath}")
        total_frames = yuvsize // framesize

        dst_fname = f"{self.tag}-{width}x{height}.yuv"
        dstpath = self.dstdir / dst_fname

        # Run
        if self.start_idx == 0 and total_frames == self.frames:
            dstpath.symlink_to(srcpath)

        elif (self.frames + self.start_idx) < total_frames:
            reader = yuvio.get_reader(srcpath, width, height, "yuv420p")
            writer = yuvio.get_writer(dstpath, width, height, "yuv420p")
            for idx in range(self.start_idx, self.frames + self.start_idx):
                yuv_frame = reader.read(idx, 1)
                writer.write(yuv_frame)

        else:
            raise ValueError(f"start_idx+frames>actual_frames: {self.start_idx}+{self.frames}>{total_frames}")
