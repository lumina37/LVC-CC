import os

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Convert40Task, CopyTask, PosetraceTask

config = update_config("config.toml")

roots = []

for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tconvert = Convert40Task(views=config.views).with_parent(tcopy)
    tposetrace = PosetraceTask(frame_per_view=6).with_parent(tconvert)

    if qps := config.QP.anchor.get(seq_name, []):
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
                tconvert = Convert40Task(views=config.views).with_parent(tcodec)
                tposetrace = PosetraceTask(frame_per_view=6).with_parent(tconvert)


if __name__ == "__main__":
    executor = Executor(roots, process_num=os.cpu_count() // 2)
    executor.run()
