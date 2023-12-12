import functools
import math
import shutil
from dataclasses import dataclass
from typing import ClassVar

from dataclasses_json import dataclass_json

from ..cfg import RaytrixCfg
from ..cfg.node import get_node_cfg
from ..logging import get_logger
from ..utils import mkdir, run_cmds
from .base import BaseTask


@dataclass_json
@dataclass
class PreprocTask(BaseTask):
    task_name: ClassVar[str] = "preproc"

    seq_name: str = ""
    crop_ratio: float = 1 / math.sqrt(2)

    @functools.cached_property
    def dirname(self) -> str:
        return f"{self.task_name}-{self.seq_name}-{self.crop_ratio:.3f}-{self.shorthash}"

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
        rlccfg.crop_ratio = self.crop_ratio

        rlccfg_dstpath = cfg_dstdir / "rlc.cfg"
        rlccfg.to_file(rlccfg_dstpath)

        # Prepare and run command
        img_srcdir = node_cfg.path.dataset / "img" / self.seq_name
        img_dstdir = self.dstdir / "img"
        mkdir(img_dstdir)

        cmds = [
            node_cfg.app.preproc,
            rlccfg_dstpath,
            img_srcdir,
            img_dstdir,
        ]
        log.info(cmds)

        run_cmds(cmds)

        self.dump_metainfo()
