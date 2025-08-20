import argparse
import shutil
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import get_any_file, mkdir
from lvccc.task import CodecTask, EncodeTask
from lvccc.utils.iterator import tasks

# Config from CMD
parser = argparse.ArgumentParser(description="Copy CodecTask *.bin to EncodeTask")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))


for tcodec in tasks(CodecTask):
    tenc = EncodeTask(qp=tcodec.qp).follow(tcodec.parent)
    mkdir(tenc.dstdir)
    tenc.dump_taskinfo(tenc.dstdir / "task.json")

    srcpath = get_any_file(tcodec.dstdir, "*.bin")
    shutil.copyfile(srcpath, tenc.dstdir / srcpath.name)
    srcpath = get_any_file(tcodec.dstdir, "*.log")
    shutil.copyfile(srcpath, tenc.dstdir / srcpath.name)
