import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CopyTask, DecodeTask, EncodeTask, PreprocTask
from lvccc.utils import avaliable_cpu_count

# Config from CMD
parser = argparse.ArgumentParser(description="Proc: codec")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
parser.add_argument("--threads", "-j", type=int, default=avaliable_cpu_count() // 2, help="use how many threads")
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))


# Task forest
roots = []

for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    crop_size = config.proc["crop_size"][seq_name]
    if qps := config.proc["QP"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)
        for qp in qps:
            tenc = EncodeTask(qp=qp).follow(tpreproc)


if __name__ == "__main__":
    executor = Executor(roots, process_num=opt.threads)
    executor.run()
