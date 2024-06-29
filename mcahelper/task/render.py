import enum
import functools
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import RLCCfg, TLCTCfg
from ..config.common import get_common_cfg
from ..config.node import get_node_cfg
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .infomap import query


class Pipeline(enum.IntEnum):
    RLC = enum.auto()
    TLCT = enum.auto()


PIPELINE_TO_CFG: dict[Pipeline, RLCCfg | TLCTCfg] = {
    Pipeline.RLC: RLCCfg,
    Pipeline.TLCT: TLCTCfg,
}


@dataclass
class RenderTask(BaseTask):
    task: str = "render"

    frames: int = 30
    views: int = 5
    pipeline: Pipeline = Pipeline.RLC

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task}-{self.seq_name}-{self.parent.shorthash}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        node_cfg = get_node_cfg()
        common_cfg = get_common_cfg()

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        # Mod and write cfg
        TypeCfg = PIPELINE_TO_CFG[self.pipeline]
        cfg_name = f"{TypeCfg.CFG_NAME}.cfg"
        rlccfg_srcpath = cfg_srcdir / cfg_name
        rlccfg = TypeCfg.from_file(rlccfg_srcpath)

        calib_cfg_name = f"{TypeCfg.CFG_NAME}.xml"
        shutil.copy(cfg_srcdir / calib_cfg_name, cfg_dstdir)
        rlccfg.Calibration_xml = str(cfg_dstdir / calib_cfg_name)
        rlccfg.RawImage_Path = str(self.srcdir / common_cfg.default_pattern)
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        rlccfg.Output_Path = str(img_dstdir / common_cfg.default_pattern.rstrip('.png'))
        rlccfg.Isfiltering = 1
        rlccfg.viewNum = self.views
        # Render frames with id \in [start, end]
        rlccfg.start_frame = 1
        rlccfg.end_frame = self.frames

        rlccfg_dstpath = cfg_dstdir / cfg_name
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command
        cmds = [
            node_cfg.app.rlc,
            rlccfg_dstpath,
        ]

        tmpwd = self.dstdir / "tmpwd"
        mkdir(tmpwd)

        run_cmds(cmds, cwd=tmpwd)
