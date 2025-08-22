from __future__ import annotations

import dataclasses as dcs
import shutil
from pathlib import Path
from typing import ClassVar

from PIL import Image

from ..config import RLC45Cfg, get_config
from ..helper import get_any_file, mkdir, run_cmds, size_from_filename
from .base import NonRootTask
from .convert import ConvertTask

IMG_PATTERN = "frame%03d"


@dcs.dataclass
class Convert45Task(ConvertTask, NonRootTask["Convert45Task"]):
    """
    Multi-view conversion (with RLC-4.5).
    """

    task: ClassVar[str] = "convert45"

    def run(self) -> None:
        config = get_config()

        # Lenslet yuv to image
        srcpath = get_any_file(self.srcdir, "*.yuv")
        ll_wdt, ll_hgt = size_from_filename(srcpath.name)

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
        rlccfg.RawImage_Path = str(srcpath)
        yuv_dir = self.dstdir / "yuv"
        mkdir(yuv_dir)

        rlccfg.Output_Path = str(yuv_dir)
        rlccfg.viewNum = self.views
        rlccfg.start_frame = 0
        rlccfg.end_frame = self.frames - 1
        rlccfg.width = ll_wdt
        rlccfg.height = ll_hgt

        rlccfg_dstpath = cfg_dstdir / cfg_name
        rlccfg.to_file(rlccfg_dstpath)

        # Convert
        convert_cmds = [
            config.app.convertor,
            rlccfg_dstpath,
        ]

        run_cmds(convert_cmds)
