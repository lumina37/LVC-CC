from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ComposeTask, RenderTask, Yuv2pngTask, YuvCopyTask

config = update_config('config.toml')

roots = []

for seq_name in config.cases.seqs:
    tcopy = YuvCopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    tyuv2png = Yuv2pngTask().with_parent(tcopy)
    trender = RenderTask().with_parent(tyuv2png)
    tcompose = ComposeTask().with_parent(trender)

    if qps := config.QP.anchor[seq_name]:
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
                tyuv2png = Yuv2pngTask().with_parent(tcodec)
                trender = RenderTask().with_parent(tyuv2png)
                tcompose = ComposeTask().with_parent(trender)


if __name__ == "__main__":
    executor = Executor(roots, process_num=1)
    executor.run()
