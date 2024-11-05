import os

from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import (
    CodecTask,
    ComposeTask,
    Img2yuvTask,
    ImgCopyTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2imgTask,
)

config = update_config('config.toml')

roots = []

for seq_name in config.cases.seqs:
    tcopy = ImgCopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tyuv2img = Yuv2imgTask().with_parent(tcopy)
    trender = RenderTask().with_parent(tyuv2img)
    tcompose = ComposeTask().with_parent(trender)

    if qps := config.QP.wMCA.get(seq_name, []):
        tpreproc = PreprocTask().with_parent(tyuv2img)
        timg2yuv = Img2yuvTask().with_parent(tpreproc)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(timg2yuv)
                tyuv2img = Yuv2imgTask().with_parent(tcodec)
                tpostproc = PostprocTask().with_parent(tyuv2img)
                trender = RenderTask().with_parent(tpostproc)
                tcompose = ComposeTask().with_parent(trender)


if __name__ == "__main__":
    executor = Executor(roots, process_num=os.cpu_count() >> 1)
    executor.run()
