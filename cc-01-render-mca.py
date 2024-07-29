from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ComposeTask, CopyTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

config = update_config('config.toml')

roots = []

for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    trender = RenderTask().with_parent(tcopy)
    tcompose = ComposeTask().with_parent(trender)

    if qps := config.QP.wMCA[seq_name]:
        tpreproc = PreprocTask().with_parent(tcopy)
        tpng2yuv = Png2yuvTask().with_parent(tpreproc)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
                tyuv2png = Yuv2pngTask().with_parent(tcodec)
                tpostproc = PostprocTask().with_parent(tyuv2png)
                trender = RenderTask().with_parent(tpostproc)
                tcompose = ComposeTask().with_parent(trender)


if __name__ == "__main__":
    executor = Executor(roots, process_num=2)
    executor.run()
