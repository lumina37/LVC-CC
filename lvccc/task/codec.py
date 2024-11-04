import dataclasses as dcs
import enum
import functools
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import mkdir, run_cmds, size_from_filename
from .base import NonRootTask
from .copy import ImgCopyTask, YuvCopyTask
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
    def tag(self) -> str:
        tag = f"{self.vtm_type}-QP{self.qp}"
        if len(self.chain) == 1 and isinstance(self.parent, YuvCopyTask):
            return "anchor-" + tag
        if len(self.chain) >= 2 and isinstance(self.chain[-2], ImgCopyTask):
            return "anchor-" + tag
        return tag

    def _run(self) -> None:
        config = get_config()
        mkdir(self.dstdir)

        vtm_type_cfg_path = Path("config") / f"vtm_{self.vtm_type}.cfg"
        vtm_type_cfg_path = vtm_type_cfg_path.absolute()

        srcpath = next(self.srcdir.glob('*.yuv'))

        width, height = size_from_filename(srcpath.name)

        dstpath_pattern = self.dstdir / self.full_tag
        log_path = dstpath_pattern.with_suffix('.log')

        with log_path.open('w', encoding='utf-8') as logf:
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
                f"{self.full_tag}.bin",
                "-o",
                f"{self.full_tag}-{width}x{height}.yuv",
            ]

            run_cmds(cmds, output=logf, cwd=self.dstdir)
