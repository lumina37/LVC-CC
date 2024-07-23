from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import (
    CodecTask,
    ComposeTask,
    CopyTask,
    Png2yuvTask,
    RenderTask,
    Yuv2pngTask,
)
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
    task1 = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tcopy)
    task2 = ComposeTask().with_parent(task1)

    # 不带MCA（不想跑就直接注释掉下面这坨）
    task1 = Png2yuvTask().with_parent(tcopy)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.woMCA[seq_name]:
            task2 = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(task1)
            task3 = Yuv2pngTask().with_parent(task2)
            task4 = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(task3)
            task5 = ComposeTask().with_parent(task4)

    # # 带MCA
    # task1 = PreprocTask().with_parent(tcopy)
    # task2 = Png2yuvTask().with_parent(task1)
    # for vtm_type in config.cases.vtm_types:
    #     for qp in config.QP.wMCA[seq_name]:
    #         task3 = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(task2)
    #         task4 = Yuv2pngTask().with_parent(task3)
    #         task5 = PostprocTask().with_parent(task4)
    #         task6 = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(task5)
    #         task7 = ComposeTask().with_parent(task6)


if __name__ == "__main__":
    executor = Executor(roots, process_num=4)
    executor.run()
