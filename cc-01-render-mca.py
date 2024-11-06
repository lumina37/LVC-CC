import os

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import (
    CodecTask,
    Img2yuvTask,
    ImgCopyTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
)

config = update_config('config.toml')

roots = []

for seq_name in config.cases.seqs:
    tcopy = ImgCopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    trender = RenderTask().with_parent(tcopy)

    if qps := config.QP.wMCA.get(seq_name, []):
        tpreproc = PreprocTask().with_parent(tcopy)
        timg2yuv = Img2yuvTask().with_parent(tpreproc)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(timg2yuv)
                tpostproc = PostprocTask().with_parent(tcodec)
                trender = RenderTask().with_parent(tpostproc)


if __name__ == "__main__":
    executor = Executor(roots, process_num=os.cpu_count() // 2)
    executor.run()
