import enum
import functools
from pathlib import Path
from typing import ClassVar

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..config import get_config
from ..helper import get_first_file, mkdir, run_cmds
from .base import NonRootTask
from .infomap import query


class VtmType(enum.StrEnum):
    AI = "AI"
    RA = "RA"


@dataclass
class CodecTask(NonRootTask["CodecTask"]):
    task: str = "codec"

    DEFAULT_QP: ClassVar[int] = -1

    vtm_type: VtmType = VtmType.RA
    qp: int = DEFAULT_QP

    @functools.cached_property
    def tag(self) -> str:
        return f"{self.vtm_type}-QP{self.qp}"

    def _run(self) -> None:
        config = get_config()
        mkdir(self.dstdir)

        vtm_type_cfg_path = Path("config") / f"vtm_{self.vtm_type}.cfg"

        refimg_path = get_first_file(self.parent.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        srcdir = query(self.parent)
        srcpath = next(srcdir.glob('*.yuv'))

        dstpath_pattern = self.dstdir / self.full_tag
        log_path = dstpath_pattern.with_suffix('.log')
        encoded_path = dstpath_pattern.with_suffix('.bin')
        decoded_path = (self.dstdir / f"{self.full_tag}-{width}x{height}").with_suffix('.yuv')

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
            f"--QP={self.qp}",
            "-i",
            srcpath,
            "-b",
            encoded_path,
            "-o",
            decoded_path,
        ]

        run_cmds(cmds, stdout_fpath=log_path)
