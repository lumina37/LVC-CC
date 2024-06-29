from mcahelper.config import set_common_cfg, set_node_cfg
from mcahelper.executor import Executor
from mcahelper.task import (
    CodecTask,
    ComposeTask,
    CopyTask,
    Png2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2pngTask,
)

common_cfg = set_common_cfg('cfg-common.toml')
node_cfg = set_node_cfg('cfg-node.toml')

roots = []

for seq_name in node_cfg.cases.seqs:
    # Anchor
    tcopy = CopyTask(seq_name=seq_name, frames=node_cfg.frames)
    roots.append(tcopy)

    task1 = RenderTask().with_parent(tcopy)
    task2 = ComposeTask().with_parent(task1)

    # W/O MCA
    task1 = Png2yuvTask().with_parent(tcopy)
    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.woMCA[seq_name]:
            task2 = CodecTask(vtm_type=vtm_type, QP=qp).with_parent(task1)
            task3 = Yuv2pngTask().with_parent(task2)
            task4 = RenderTask().with_parent(task3)
            task5 = ComposeTask().with_parent(task4)

    # W MCA
    task1 = PreprocTask().with_parent(tcopy)
    task2 = Png2yuvTask().with_parent(task1)
    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.wMCA[seq_name]:
            task3 = CodecTask(vtm_type=vtm_type, QP=qp).with_parent(task2)
            task4 = Yuv2pngTask().with_parent(task3)
            task5 = PostprocTask().with_parent(task4)
            task6 = RenderTask().with_parent(task5)
            task7 = ComposeTask().with_parent(task6)


if __name__ == "__main__":
    executor = Executor(roots, process_num=4)
    executor.run()
