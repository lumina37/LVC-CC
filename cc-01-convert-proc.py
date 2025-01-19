import sys

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask
from lvccc.utils import avaliable_cpu_count

config_fname = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
config = update_config(config_fname)

roots = []

for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tconvert = Convert40Task(views=config.views).with_parent(tcopy)

    if qps := config.QP.proc.get(seq_name, []):
        tpreproc = PreprocTask().with_parent(tcopy)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpreproc)
                tpostproc = PostprocTask().with_parent(tcodec)
                tconvert = Convert40Task(views=config.views).with_parent(tpostproc)


if __name__ == "__main__":
    executor = Executor(roots, process_num=avaliable_cpu_count() // 2)
    executor.run()
