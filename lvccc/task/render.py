import dataclasses as dcs
import enum
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import RenderCfg, get_config
from ..helper import mkdir, run_cmds
from .base import NonRootTask
from .copy import ImgCopyTask, YuvCopyTask
from .infomap import query


class Pipeline(enum.IntEnum):
    NOTSET = -1
    RLC = 0
    TLCT = 1


PIPELINE_TO_CFG: dict[Pipeline, RenderCfg] = {
    Pipeline.RLC: RenderCfg,
    Pipeline.TLCT: RenderCfg,
}


@dcs.dataclass
class RenderTask(NonRootTask["RenderTask"]):
    task: ClassVar[str] = "render"

    views: int = 0
    pipeline: Pipeline = Pipeline.NOTSET

    def _post_with_parent(self) -> None:
        super()._post_with_parent()
        if self.pipeline == Pipeline.NOTSET:
            config = get_config()
            pipeline = Pipeline(config.pipeline[self.seq_name])
            self.pipeline = pipeline
        if self.views == 0:
            config = get_config()
            self.views = config.views

    @functools.cached_property
    def tag(self) -> str:
        if len(self.chain) == 1 and isinstance(self.parent, ImgCopyTask):
            return "base"
        if len(self.chain) >= 2 and isinstance(self.chain[-2], YuvCopyTask):
            return "base"
        return ""

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
        cfg_name = "param.cfg"
        rlccfg_srcpath = cfg_srcdir / cfg_name
        rlccfg = TypeCfg.from_file(rlccfg_srcpath)

        calib_cfg_name = "calib.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        rlccfg.pipeline = self.pipeline
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

        run_cmds(cmds)
