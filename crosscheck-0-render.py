from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ComposeTask, CopyTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask
from lvccc.task.render import Pipeline

name2pipeline = {
    "Boxer-IrishMan-Gladiator": Pipeline.RLC,
    "ChessPieces": Pipeline.RLC,
    "NagoyaFujita": Pipeline.RLC,
    "Boys": Pipeline.TLCT,
    "Matryoshka": Pipeline.TLCT,
}

# 从指定路径加载config
config = update_config('config.toml')

# 根任务
# Executor会执行所有根任务和子结点任务
roots = []

for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    roots.append(tcopy)

    # Anchor
    trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tcopy)
    tcompose = ComposeTask().with_parent(trender)

    # 不带MCA（不想跑就直接注释掉下面这坨）
    if qps := config.QP.woMCA[seq_name]:
        tpng2yuv = Png2yuvTask().with_parent(tcopy)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
                tyuv2png = Yuv2pngTask().with_parent(tcodec)
                trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tyuv2png)
                tcompose = ComposeTask().with_parent(trender)

    # 带MCA
    if qps := config.QP.wMCA[seq_name]:
        tpreproc = PreprocTask().with_parent(tcopy)
        tpng2yuv = Png2yuvTask().with_parent(tpreproc)
        for vtm_type in config.cases.vtm_types:
            for qp in qps:
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
                tyuv2png = Yuv2pngTask().with_parent(tcodec)
                tpostproc = PostprocTask().with_parent(tyuv2png)
                trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tpostproc)
                tcompose = ComposeTask().with_parent(trender)


if __name__ == "__main__":
    executor = Executor(roots, process_num=2)
    executor.run()
