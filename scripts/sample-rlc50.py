import argparse
import shutil
from pathlib import Path

import yuvio

from lvccc.config import CalibCfg, RLC45Cfg, update_config
from lvccc.helper import get_any_file, mkdir

parser = argparse.ArgumentParser(description="Sample Sequences for RLC50")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

# 读取配置
config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

for seq_name in config.seqs:
    tlct_cfg_path = Path("config") / seq_name / "tlct" / "calib.cfg"
    rlc50_calib_path = Path("config") / seq_name / "rlc50" / "calib.xml"
    rlc50_param_path = Path("config") / seq_name / "rlc50" / "param.cfg"

    tlct_cfg = CalibCfg.from_file(tlct_cfg_path)

    width = tlct_cfg.LensletWidth
    height = tlct_cfg.LensletHeight

    yuv_srcdir = config.dir.input / seq_name
    yuv_srcpath = get_any_file(yuv_srcdir, "*.yuv")

    dstdir = config.dir.output / "sample-rlc50" / seq_name
    mkdir(dstdir)

    cfg_dstdir = dstdir / "cfg"
    mkdir(cfg_dstdir)

    yuv_dstdir = dstdir / "yuv"
    mkdir(yuv_dstdir)

    calib_dst = cfg_dstdir / "calib.xml"
    shutil.copyfile(rlc50_calib_path, calib_dst)

    rlccfg = RLC45Cfg.from_file(rlc50_param_path)

    rlccfg.Calibration_xml = "cfg/calib.xml"
    rlccfg.RawImage_Path = "src.yuv"
    rlccfg.Output_Path = "./yuv"

    rlccfg.viewNum = config.views
    rlccfg.start_frame = 0
    rlccfg.end_frame = config.frames - 1
    rlccfg.width = width
    rlccfg.height = height

    param_dst = cfg_dstdir / "param.cfg"
    rlccfg.to_file(param_dst)

    yuv_dstpath = dstdir / "src.yuv"

    reader = yuvio.get_reader(yuv_srcpath, width, height, "yuv420p")
    writer = yuvio.get_writer(yuv_dstpath, width, height, "yuv420p")

    for idx in range(config.frames):
        yuv_frame = reader.read(idx, 1)
        writer.write(yuv_frame)
