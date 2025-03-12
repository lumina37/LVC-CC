import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask
from lvccc.utils import avaliable_cpu_count

parser = argparse.ArgumentParser(description="Proc: convert/preproc+codec+postproc+convert")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base",
    "-b",
    type=str,
    default="base.toml",
    help="base config, recommend to store some immutable directory settings",
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

roots = []

for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tconvert = Convert40Task(views=config.views).follow(tcopy)

    if qps := config.proc["QP"].get(seq_name, []):
        tpreproc = PreprocTask().follow(tcopy)
        for qp in qps:
            tcodec = CodecTask(qp=qp).follow(tpreproc)
            tpostproc = PostprocTask().follow(tcodec)
            tconvert = Convert40Task(views=config.views).follow(tpostproc)


if __name__ == "__main__":
    executor = Executor(roots, process_num=avaliable_cpu_count() // 2)
    executor.run()
