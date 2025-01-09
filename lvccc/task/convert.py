import dataclasses as dcs
import functools
import shutil
from pathlib import Path
from typing import ClassVar

from ..config import get_config
from ..helper import get_any_file, mkdir, run_cmds
from .base import NonRootTask
from .copy import CopyTask
from .infomap import query


@dcs.dataclass
class ConvertTask(NonRootTask["ConvertTask"]):
    task: ClassVar[str] = "convert"

    views: int = 1

    @functools.cached_property
    def self_tag(self) -> str:
        if isinstance(self.parent, CopyTask):
            return "base"
        return ""

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _inner_run(self) -> None:
        config = get_config()

        cfg_srcdir = Path("config") / self.seq_name

        calib_cfg_name = "calib.cfg"
        calib_cfg_dstpath = self.dstdir / calib_cfg_name
        shutil.copyfile(cfg_srcdir / calib_cfg_name, calib_cfg_dstpath)

        with (cfg_srcdir / "cmd.sh").open(encoding="utf-8") as f:
            extra_args = f.read().rstrip("\n").split(" ")

        yuv_srcpath = get_any_file(self.srcdir, "*.yuv")
        yuv_dstdir = self.dstdir / "yuv"
        mkdir(yuv_dstdir)

        cmds = [
            config.app.convertor,
            calib_cfg_dstpath,
            "-i",
            yuv_srcpath,
            "-o",
            yuv_dstdir,
            "--end",
            self.frames,
            "--views",
            self.views,
            *extra_args,
        ]

        run_cmds(cmds)

        for yuv_path in list(yuv_dstdir.iterdir()):
            new_fname = f"{self.tag}-{yuv_path.name}"
            yuv_path.rename(yuv_path.with_name(new_fname))
