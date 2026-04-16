from __future__ import annotations

import dataclasses as dcs
import functools
import re
import shutil
import subprocess
from pathlib import Path
from typing import ClassVar

from ..config import CalibCfg, RLC50Cfg, get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .convert import ConvertTask


@dcs.dataclass
class Convert50Task(ConvertTask, NonRootTask["Convert50Task"]):
    """
    Multi-view conversion (with RLC-5.0).
    """

    task: ClassVar[str] = "convert50"

    @functools.cached_property
    def tlct_calib_cfg_path(self) -> Path:
        return Path("config") / self.seq_name / "tlct" / "calib.cfg"

    @functools.cached_property
    def calib_cfg_path(self) -> Path:
        return Path("config") / self.seq_name / "rlc50" / "calib.xml"

    @functools.cached_property
    def param_cfg_path(self) -> Path:
        return Path("config") / self.seq_name / "rlc50" / "param.cfg"

    def run(self) -> None:
        config = get_config()

        tlct_cfg = CalibCfg.from_file(self.tlct_calib_cfg_path)

        # Prepare
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        rlccfg = RLC50Cfg.from_file(self.param_cfg_path)

        cfg_dstpath = cfg_dstdir / "calib.xml"
        shutil.copyfile(self.calib_cfg_path, cfg_dstpath)
        rlccfg.Calibration_xml = str(cfg_dstpath)
        yuv_srcpath = str(get_any_file(self.srcdir, "*.yuv"))
        rlccfg.RawImage_Path = yuv_srcpath
        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)

        rlccfg.Output_Path = str(yuv_dstdir)
        rlccfg.viewNum = self.views
        rlccfg.start_frame = 0
        rlccfg.end_frame = self.frames - 1
        rlccfg.width = tlct_cfg.LensletWidth
        rlccfg.height = tlct_cfg.LensletHeight

        rlccfg_dstpath = cfg_dstdir / "param.cfg"
        rlccfg.to_file(rlccfg_dstpath)

        # Convert
        convert_cmds = [
            config.app.convertor.RLC50,
            rlccfg_dstpath,
        ]

        cmd_result = run_cmds(convert_cmds, output=subprocess.PIPE)

        mvsize_matchobj = re.search(r"(\d+) x (\d+)", cmd_result.stdout)
        mv_wdt = int(mvsize_matchobj.group(1))
        mv_hgt = int(mvsize_matchobj.group(2))

        for view, yuv_path in enumerate(sorted(yuv_dstdir.iterdir())):
            new_fname = f"{self.tag}-v{view:0>3}-{mv_wdt}x{mv_hgt}.yuv"
            yuv_path.rename(yuv_path.with_name(new_fname))
