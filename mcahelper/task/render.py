import functools
import shutil
from pathlib import Path

from pydantic.dataclasses import dataclass

from ..cfg import RaytrixCfg
from ..cfg.node import get_node_cfg
from ..logging import get_logger
from ..utils import get_first_file, get_src_pattern, mkdir, run_cmds
from .base import BaseTask
from .infomap import query


@dataclass
class RenderTask(BaseTask):
    task: str = "render"

    frames: int = 30
    views: int = 5

    @functools.cached_property
    def dirname(self) -> str:
        if self.pretask:
            return f"{self.task}-{self.seq_name}-{self.views}-{self.pretask.shorthash}-{self.shorthash}"
        else:
            return f"{self.task}-{self.seq_name}-{self.views}-{self.shorthash}"

    @functools.cached_property
    def srcdir(self) -> Path:
        if self.pretask:
            srcdir = query(self.pretask) / "img"
        else:
            node_cfg = get_node_cfg()
            srcdir = node_cfg.path.dataset / "img" / self.seq_name
        return srcdir

    def run(self) -> None:
        log = get_logger()
        node_cfg = get_node_cfg()

        # Copy `calibration.xml`
        cfg_srcdir = node_cfg.path.dataset / "cfg" / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)
        shutil.copy(cfg_srcdir / "calibration.xml", cfg_dstdir)

        # Mod and write `rlc.cfg`
        rlccfg_srcpath = cfg_srcdir / "rlc.cfg"
        rlccfg = RaytrixCfg.from_file(rlccfg_srcpath)

        rlccfg.Calibration_xml = str(cfg_dstdir / "calibration.xml")
        fname_pattern = get_src_pattern(get_first_file(self.srcdir).name)
        rlccfg.RawImage_Path = str(self.srcdir / fname_pattern)
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)
        rlccfg.Output_Path = str(img_dstdir / "frame#%03d")
        rlccfg.Isfiltering = 1
        rlccfg.end_frame = self.frames

        rlccfg_dstpath = cfg_dstdir / "rlc.cfg"
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command

        cmds = [
            node_cfg.app.rlc,
            rlccfg_dstpath,
        ]

        run_cmds(cmds)
        log.info(f"Completed! cmds={cmds}")

        self.dump_metainfo()
