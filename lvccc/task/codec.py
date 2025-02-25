from __future__ import annotations

import dataclasses as dcs
import enum
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds, size_from_filename
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


class VtmType(enum.StrEnum):
    AI = "AI"
    RA = "RA"


@dcs.dataclass
class CodecTask(NonRootTask["CodecTask"]):
    """
    VVC Codec (with VTM-11.0).
    """

    task: ClassVar[str] = "codec"

    DEFAULT_QP: ClassVar[int] = -1

    vtm_type: VtmType = VtmType.RA
    qp: int = DEFAULT_QP

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    @functools.cached_property
    def self_tag(self) -> str:
        tag = f"{self.vtm_type}-QP{self.qp}"
        if isinstance(self.parent, CopyTask):
            return "anchor-" + tag
        return tag

    def _inner_run(self) -> None:
        # Prepare
        config = get_config()

        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        vtm_cfg_srcpath = Path("config") / f"vtm_{self.vtm_type}.cfg"
        vtm_cfg_dstpath = cfg_dstdir / "type.cfg"
        shutil.copy(vtm_cfg_srcpath, vtm_cfg_dstpath)
        seq_cfg_srcpath = Path("config") / self.seq_name / "codec.cfg"
        seq_cfg_dstpath = cfg_dstdir / "seq.cfg"
        shutil.copy(seq_cfg_srcpath, seq_cfg_dstpath)

        srcpath = get_any_file(self.srcdir, "*.yuv")
        width, height = size_from_filename(srcpath.name)

        dstpath_pattern = self.dstdir / self.tag
        log_path = dstpath_pattern.with_suffix(".log")

        # Run
        with log_path.open("w", encoding="utf-8") as logf:
            cmds = [
                config.app.encoder,
                "-c",
                vtm_cfg_dstpath.relative_to(self.dstdir),
                "-c",
                seq_cfg_dstpath.relative_to(self.dstdir),
                "-wdt",
                width,
                "-hgt",
                height,
                f"--FramesToBeEncoded={self.frames}",
                f"--QP={self.qp}",
                "-i",
                srcpath,
                "-b",
                f"{self.tag}.bin",
                "-o",
                f"{self.tag}-{width}x{height}.yuv",
            ]

            run_cmds(cmds, output=logf, cwd=self.dstdir)
