import argparse
import shutil
from pathlib import Path

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.helper import get_any_file, mkdir
from lvccc.task import CodecTask, CopyTask, EncodeTask

# Config from CMD
parser = argparse.ArgumentParser(description="Time it")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))


# Task forest
roots = []

for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    for qp in config.anchorQP.get(seq_name, []):
        tcodec = CodecTask(qp=qp).follow(tcopy)
        tenc = EncodeTask(qp=qp).follow(tcopy)
        mkdir(tenc.dstdir)
        tenc.run()
        tenc.dump_taskinfo(tenc.dstdir / "task.json")

        srcpath = get_any_file(tcodec.dstdir, "*.bin")
        shutil.copyfile(srcpath, tenc.dstdir / srcpath.name)
        srcpath = get_any_file(tcodec.dstdir, "*.log")
        shutil.copyfile(srcpath, tenc.dstdir / srcpath.name)


if __name__ == "__main__":
    executor = Executor(roots, process_num=1)
    executor.run()
