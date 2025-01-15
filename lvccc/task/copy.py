import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

import yuvio

from ..config import CalibCfg, get_config
from ..helper import MD5Cache, compute_md5, get_any_file, get_md5, mtime
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
        # Check MD5
        config = get_config()

        srcdir = config.dir.input / self.seq_name
        srcpath = get_any_file(srcdir, "*.yuv")

        cfg_srcdir = Path("config") / self.seq_name
        md5_path = cfg_srcdir / "checksum.md5"
        except_md5 = get_md5(md5_path)
        md5_cache = MD5Cache()
        cached_mtime = md5_cache[except_md5]
        if (yuv_mtime := mtime(srcpath)) > cached_mtime:
            md5 = compute_md5(srcpath)
            if md5 != except_md5:
                logger = get_logger()
                logger.warning(f"MD5 checksum does not match for {srcpath}")
            else:
                md5_cache[md5] = yuv_mtime

        # Prepare
        with (cfg_srcdir / "calib.cfg").open(encoding="utf-8") as f:
            calib_cfg = CalibCfg.load(f)

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
