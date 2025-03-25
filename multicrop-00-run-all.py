import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask
from lvccc.utils import avaliable_cpu_count

parser = argparse.ArgumentParser(description="Proc with multi crop_sizes")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
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

    for anchorQP in config.anchorQP.get(seq_name, []):
        tcodec = CodecTask(qp=anchorQP).follow(tcopy)
        tconvert = Convert40Task(views=config.views).follow(tcodec)

    startQP = config.proc.get("startQP", 0)
    endQP = config.proc.get("endQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)
        for anchorQP in config.anchorQP.get(seq_name, []):
            for offsetQP in range(startQP, endQP):
                qp = anchorQP + offsetQP
                tcodec = CodecTask(qp=qp).follow(tpreproc)
                tpostproc = PostprocTask().follow(tcodec)
                tconvert = Convert40Task(views=config.views).follow(tpostproc)


if __name__ == "__main__":
    executor = Executor(roots, process_num=avaliable_cpu_count() // 2)
    executor.run()
