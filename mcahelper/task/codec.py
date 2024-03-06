import functools

import cv2 as cv
from pydantic.dataclasses import dataclass

from ..cfg.node import get_node_cfg
from ..cfg.vtm import VTMCfg
from ..utils import get_first_file, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class CodecTask(BaseTask):
    task: str = "codec"

    vtm_type: str = ""  # `AI` or `RA`
    frames: int = 30
    QP: int = 40

    @functools.cached_property
    def dirname(self) -> str:
        assert self.parent is not None
        return f"{self.task}-{self.seq_name}-{self.vtm_type}-{self.QP}-{self.parent.shorthash}-{self.shorthash}"

    def _run(self) -> None:
        node_cfg = get_node_cfg()

        assert self.vtm_type in ['AI', 'RA']
        vtm_type_cfg_path = node_cfg.path.dataset / "cfg" / f"vtm_{self.vtm_type}.cfg"

        refimg_path = get_first_file(self.parent.srcdir)
        refimg = cv.imread(str(refimg_path))
        height, width = refimg.shape[:2]

        vtmcfg_srcpath = node_cfg.path.dataset / "cfg" / self.seq_name / "vtm.cfg"
        vtm_cfg = VTMCfg.from_file(vtmcfg_srcpath)
        vtm_cfg.SourceHeight = height
        vtm_cfg.SourceWidth = width

        mkdir(self.dstdir)
        vtmcfg_dstpath = self.dstdir / 'vtm.cfg'
        vtm_cfg.to_file(vtmcfg_dstpath)

        srcdir = query(self.parent)
        srcpath = srcdir / "out.yuv"

        log_path = self.dstdir / "out.log"
        encoded_path = self.dstdir / "out.bin"
        decoded_path = self.dstdir / "out.yuv"

        cmds = [
            node_cfg.app.encoder,
            "-c",
            vtm_type_cfg_path,
            "-c",
            vtmcfg_dstpath,
            "--InternalBitDepth=10",
            "--OutputBitDepth=8",
            f"--FramesToBeEncoded={self.frames}",
            "--TemporalSubsampleRatio=1",
            f"--QP={self.QP}",
            "-i",
            srcpath,
            "-b",
            encoded_path,
            "-o",
            decoded_path,
        ]

        run_cmds(cmds, stdout_fpath=log_path)
