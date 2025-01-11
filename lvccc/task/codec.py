import dataclasses as dcs
import enum
import functools
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, run_cmds, size_from_filename
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


class VtmType(enum.StrEnum):
    AI = "AI"
    RA = "RA"


@dcs.dataclass
class CodecTask(NonRootTask["CodecTask"]):
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

        vtm_type_cfg_path = Path("config") / f"vtm_{self.vtm_type}.cfg"
        vtm_type_cfg_path = vtm_type_cfg_path.absolute()

        srcpath = get_any_file(self.srcdir, "*.yuv")
        width, height = size_from_filename(srcpath.name)

        dstpath_pattern = self.dstdir / self.tag
        log_path = dstpath_pattern.with_suffix(".log")

        # Run
        with log_path.open("w", encoding="utf-8") as logf:
            cmds = [
                config.app.encoder,
                "-c",
                vtm_type_cfg_path,
                "-wdt",
                width,
                "-hgt",
                height,
                "-fr",
                30,
                "--InputBitDepth=8",
                "--OutputBitDepth=8",
                f"--FramesToBeEncoded={self.frames}",
                "--Level=6.2",
                "--ConformanceMode=1",
                f"--QP={self.qp}",
                "-i",
                srcpath,
                "-b",
                f"{self.tag}.bin",
                "-o",
                f"{self.tag}-{width}x{height}.yuv",
            ]

            run_cmds(cmds, output=logf, cwd=self.dstdir)
