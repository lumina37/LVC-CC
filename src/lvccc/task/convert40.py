from __future__ import annotations

import dataclasses as dcs
import shutil
from pathlib import Path
from typing import ClassVar

from PIL import Image

from ..config import CalibCfg, RLC40Cfg, get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .convert import ConvertTask

IMG_PATTERN = "frame%03d"


@dcs.dataclass
class Convert40Task(ConvertTask, NonRootTask["Convert40Task"]):
    """
    Multi-view conversion (with RLC-4.0).
    """

    task: ClassVar[str] = "convert40"

    def run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        tlct_cfg_srcpath = cfg_srcdir / "calib.cfg"
        tlct_cfg = CalibCfg.from_file(tlct_cfg_srcpath)

        # Lenslet yuv to image
        srcpath = get_any_file(self.srcdir, "*.yuv")
        img_srcdir = self.dstdir / "img" / "src"
        mkdir(img_srcdir)
        img_src_pattern = (img_srcdir / IMG_PATTERN).with_suffix(".png")

        yuv2img_cmds = [
            config.app.ffmpeg,
            "-f",
            "rawvideo",
            "-s",
            f"{tlct_cfg.LensletWidth}x{tlct_cfg.LensletHeight}",
            "-i",
            srcpath,
            "-frames:v",
            self.frames,
            img_src_pattern,
            "-v",
            "error",
            "-y",
        ]

        run_cmds(yuv2img_cmds)

        # Prepare
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        cfg_name = "param.cfg"
        rlccfg_srcpath = cfg_srcdir / cfg_name
        rlccfg = RLC40Cfg.from_file(rlccfg_srcpath)

        calib_cfg_name = "calib.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        rlccfg.Calibration_xml = str(cfg_dstpath)
        rlccfg.RawImage_Path = str(img_src_pattern)
        img_dstdir = self.dstdir / "img" / "dst"
        mkdir(img_dstdir)

        rlccfg.Output_Path = str(img_dstdir / IMG_PATTERN)
        rlccfg.viewNum = self.views
        rlccfg.start_frame = 1
        rlccfg.end_frame = self.frames
        rlccfg.width = tlct_cfg.LensletWidth
        rlccfg.height = tlct_cfg.LensletHeight

        rlccfg_dstpath = cfg_dstdir / cfg_name
        rlccfg.to_file(rlccfg_dstpath)

        # Convert
        convert_cmds = [
            config.app.convertor.RLC40,
            rlccfg_dstpath,
        ]

        run_cmds(convert_cmds)

        # Multi-view image to yuv
        yuv_dir = self.dstdir / "yuv"
        mkdir(yuv_dir)

        refimg_path = get_any_file(next(img_dstdir.iterdir()), "*.png")
        refimg = Image.open(refimg_path)
        mv_wdt, mv_hgt = refimg.size

        for view in range(self.views**2):
            img2yuv_cmds = [
                config.app.ffmpeg,
                "-i",
                img_dstdir / IMG_PATTERN / f"image_{view + 1:0>3}.png",
                "-vf",
                "format=yuv420p",
                "-frames:v",
                self.frames,
                yuv_dir / f"{self.tag}-v{view:0>3}-{mv_wdt}x{mv_hgt}.yuv",
                "-v",
                "error",
                "-y",
            ]

            run_cmds(img2yuv_cmds)
