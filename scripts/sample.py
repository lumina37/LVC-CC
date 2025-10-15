import argparse
import shutil
from pathlib import Path

import yuvio

from lvccc.config import CalibCfg, update_config
from lvccc.helper import get_any_file, mkdir

parser = argparse.ArgumentParser(description="Sample Sequences for Demo")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

for seq_name in config.seqs:
    cfg_srcdir = Path("config") / seq_name
    calib_cfg = CalibCfg.from_file(cfg_srcdir / "calib.cfg")

    width = calib_cfg.LensletWidth
    height = calib_cfg.LensletHeight
    framesize = width * height // 2 * 3

    yuv_srcdir = config.dir.input / seq_name
    yuv_srcpath = get_any_file(yuv_srcdir, "*.yuv")
    dstdir = config.dir.output / "sample" / seq_name
    mkdir(dstdir)
    yuv_dstpath = dstdir / "src.yuv"
    shutil.copyfile(cfg_srcdir / "calib.cfg", dstdir / "calib.cfg")

    reader = yuvio.get_reader(yuv_srcpath, width, height, "yuv420p")
    writer = yuvio.get_writer(yuv_dstpath, width, height, "yuv420p")
    for idx in range(config.frames):
        yuv_frame = reader.read(idx, 1)
        writer.write(yuv_frame)
