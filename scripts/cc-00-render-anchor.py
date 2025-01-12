import os

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ConvertTask, CopyTask

config = update_config("config.toml")

roots = []

for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tconvert = ConvertTask(views=config.views).with_parent(tcopy)

    if qps := config.QP.anchor.get(seq_name, []):
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
                tconvert = ConvertTask(views=config.views).with_parent(tcodec)


if __name__ == "__main__":
    executor = Executor(roots, process_num=os.cpu_count() // 2)
    executor.run()
