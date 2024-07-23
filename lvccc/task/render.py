import enum
import functools
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..config import RLCCfg, TLCTCfg, get_config
from ..utils import mkdir, run_cmds
from .base import BaseTask
from .copy import CopyTask
from .infomap import query


class Pipeline(enum.IntEnum):
    RLC = enum.auto()
    TLCT = enum.auto()


PIPELINE_TO_CFG: dict[Pipeline, RLCCfg | TLCTCfg] = {
    Pipeline.RLC: RLCCfg,
    Pipeline.TLCT: TLCTCfg,
}


@dataclass
class RenderTask(BaseTask["RenderTask"]):
    task: str = "render"

    frames: int = 0
    views: int = 5
    pipeline: Pipeline = Pipeline.RLC

    @functools.cached_property
    def dirname(self) -> str:
        return "base" if isinstance(self.parent, CopyTask) else ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent) / "img"
        return srcdir

    def _run(self) -> None:
        config = get_config()

        # Copy `calibration.xml`
        cfg_srcdir = Path("config") / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        # Mod and write cfg
        TypeCfg = PIPELINE_TO_CFG[self.pipeline]
        cfg_name = f"{TypeCfg.CFG_NAME}.cfg"
        rlccfg_srcpath = cfg_srcdir / cfg_name
        rlccfg = TypeCfg.from_file(rlccfg_srcpath)

        calib_cfg_name = f"{TypeCfg.CFG_NAME}.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        rlccfg.Calibration_xml = str(cfg_dstpath)
        rlccfg.RawImage_Path = str(self.srcdir / config.default_pattern)
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        rlccfg.Output_Path = str(img_dstdir / config.default_pattern.rstrip('.png'))
        rlccfg.viewNum = self.views
        # Render frames with id \in [start, end]
        rlccfg.start_frame = 1
        rlccfg.end_frame = self.frames

        rlccfg_dstpath = cfg_dstdir / cfg_name
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command
        cmds = [
            config.app.rlc,
            rlccfg_dstpath,
        ]

        if self.pipeline == Pipeline.RLC:
            tmpwd = self.dstdir / "tmpwd"
            mkdir(tmpwd)
        else:
            tmpwd = None

        run_cmds(cmds, cwd=tmpwd)
