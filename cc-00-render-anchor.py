from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ComposeTask, ImgCopyTask, Png2yuvTask, RenderTask, Yuv2pngTask

config = update_config('config.toml')

roots = []

for seq_name in config.cases.seqs:
    tcopy = ImgCopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    trender = RenderTask().with_parent(tcopy)
    tcompose = ComposeTask().with_parent(trender)

    if qps := config.QP.anchor[seq_name]:
        tpng2yuv = Png2yuvTask().with_parent(tcopy)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
                tyuv2png = Yuv2pngTask().with_parent(tcodec)
                trender = RenderTask().with_parent(tyuv2png)
                tcompose = ComposeTask().with_parent(trender)


if __name__ == "__main__":
    executor = Executor(roots, process_num=1)
    executor.run()
