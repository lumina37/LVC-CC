from __future__ import annotations

import dataclasses as dcs
import functools
import shutil
import time
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, mkdir, remove, run_cmds, size_from_filename
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


@dcs.dataclass
class EncodeTask(NonRootTask["EncodeTask"]):
    """
    VVC Encode (with VTM-11.0).
    """

    task: ClassVar[str] = "encode"

    qp: int = 0

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    @functools.cached_property
    def self_tag(self) -> str:
        tag = f"QP{self.qp}"
        if isinstance(self.parent, CopyTask):
            return "anchor-" + tag
        return tag

    def run(self) -> None:
        # Fast path
        bitstream_dstname = f"{self.tag}.bin"

        if self.frames == 300 and isinstance(self.parent, CopyTask):
            bitstream_bundled_path = Path("bitstream/vvc") / f"{self.seq_name}_qp{self.qp}.bin"
            if bitstream_bundled_path.exists():
                mkdir(self.dstdir)
                shutil.copyfile(bitstream_bundled_path, self.dstdir / bitstream_dstname)
                time.sleep(1.0)  # To wait fs flush
                return

        # Prepare
        config = get_config()

        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        vtm_ra_cfg_srcpath = Path("config") / "vtmRA.cfg"
        vtm_ra_cfg_dstpath = cfg_dstdir / "vtm.cfg"
        shutil.copyfile(vtm_ra_cfg_srcpath, vtm_ra_cfg_dstpath)
        vtm_extra_cfg_srcpath = Path("config") / self.seq_name / "codec.cfg"
        vtm_extra_cfg_dstpath = cfg_dstdir / "vtmExtra.cfg"
        shutil.copyfile(vtm_extra_cfg_srcpath, vtm_extra_cfg_dstpath)

        srcpath = get_any_file(self.srcdir, "*.yuv")
        width, height = size_from_filename(srcpath.name)

        dstpath_pattern = self.dstdir / self.tag
        log_path = dstpath_pattern.with_suffix(".log")

        # Run
        with log_path.open("w", encoding="utf-8") as logf:
            cmds = [
                config.app.encoder,
                "-c",
                vtm_ra_cfg_dstpath.relative_to(self.dstdir),
                "-c",
                vtm_extra_cfg_dstpath.relative_to(self.dstdir),
                "-wdt",
                width,
                "-hgt",
                height,
                f"--FramesToBeEncoded={self.frames}",
                f"--QP={self.qp}",
                "-i",
                srcpath,
                "-b",
                bitstream_dstname,
            ]

            run_cmds(cmds, output=logf, cwd=self.dstdir)

        remove(self.dstdir / "rec.yuv")
