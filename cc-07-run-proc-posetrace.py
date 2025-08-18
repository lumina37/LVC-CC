import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import Convert40Task, CopyTask, DecodeTask, EncodeTask, PosetraceTask, PostprocTask, PreprocTask
from lvccc.utils import avaliable_cpu_count

# Config from CMD
parser = argparse.ArgumentParser(description="Proc: posetrace")

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
            tdec = DecodeTask().follow(tenc)
            tpostproc = PostprocTask().follow(tdec)
            tconvert = Convert40Task(views=config.views).follow(tpostproc)
            tposetrace = PosetraceTask(frame_per_view=12).follow(tconvert)


if __name__ == "__main__":
    executor = Executor(roots, process_num=opt.threads)
    executor.run()
