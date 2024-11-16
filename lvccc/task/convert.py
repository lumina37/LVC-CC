import dataclasses as dcs
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import ConvertCfg, get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .copy import ImgCopyTask, YuvCopyTask
from .infomap import query


@dcs.dataclass
class ConvertTask(NonRootTask["ConvertTask"]):
    task: ClassVar[str] = "convert"

    views: int = 0

    def _post_with_parent(self) -> None:
        super()._post_with_parent()
        if self.views == 0:
            config = get_config()
            self.views = config.views

    @functools.cached_property
    def self_tag(self) -> str:
        if len(self.chain) == 1 and isinstance(self.parent, YuvCopyTask):
            return "base"
        if len(self.chain) >= 2 and isinstance(self.chain[-2], ImgCopyTask):
            return "base"
        return ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _inner_run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name
        cfg_dstdir = self.dstdir / "cfg"
        mkdir(cfg_dstdir)

        cfg_name = "param.cfg"
        cvtcfg_srcpath = cfg_srcdir / cfg_name
        cvtcfg = ConvertCfg.from_file(cvtcfg_srcpath)

        calib_cfg_name = "calib.xml"
        cfg_dstpath = cfg_dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, cfg_dstpath)
        cvtcfg.calibFile = str(cfg_dstpath)

        yuv_srcpath = get_any_file(self.srcdir, '*.yuv')
        cvtcfg.inFile = str(yuv_srcpath)

        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)
        cvtcfg.outDir = str(yuv_dstdir)

        cvtcfg.views = self.views
        cvtcfg.frameBegin = 0
        cvtcfg.frameEnd = self.frames

        cvtcfg_dstpath = cfg_dstdir / cfg_name
        cvtcfg.to_file(cvtcfg_dstpath)

        cmds = [
            config.app.convertor,
            cvtcfg_dstpath,
        ]

        run_cmds(cmds)

        for yuv_path in list(yuv_dstdir.iterdir()):
            new_fname = f"{self.tag}-{yuv_path.name}"
            yuv_path.rename(yuv_path.with_name(new_fname))
