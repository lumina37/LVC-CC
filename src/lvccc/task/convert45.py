from __future__ import annotations

import dataclasses as dcs
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import CalibCfg, RLC45Cfg, get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .convert import ConvertTask


@dcs.dataclass
class Convert45Task(ConvertTask, NonRootTask["Convert45Task"]):
    """
    Multi-view conversion (with RLC-4.5, YUV420 I/O).
    """

    task: ClassVar[str] = "convert45"

    def run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        tlct_cfg_srcpath = cfg_srcdir / "calib.cfg"
        tlct_cfg = CalibCfg.from_file(tlct_cfg_srcpath)

        # Prepare
        cfg_srcdir = Path("config") / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        cfg_name = "param.cfg"
        rlccfg_srcpath = cfg_srcdir / cfg_name
        rlccfg = RLC45Cfg.from_file(rlccfg_srcpath)

        calib_cfg_name = "calib.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        rlccfg.Calibration_xml = str(cfg_dstpath)
        rlccfg.RawImage_Path = str(get_any_file(self.srcdir, "*.yuv"))
        yuv_dir = self.dstdir / "yuv"
        mkdir(yuv_dir)

        rlccfg.Output_Path = str(yuv_dir)
        rlccfg.viewNum = self.views
        rlccfg.start_frame = 0
        rlccfg.end_frame = self.frames - 1
        rlccfg.width = tlct_cfg.LensletWidth
        rlccfg.height = tlct_cfg.LensletHeight

        rlccfg_dstpath = cfg_dstdir / cfg_name
        rlccfg.to_file(rlccfg_dstpath)

        # Convert
        convert_cmds = [
            config.app.convertor.RLC45,
            rlccfg_dstpath,
        ]

        run_cmds(convert_cmds)
