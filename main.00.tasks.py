from mcahelper.config import common, node
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, CopyTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

node_cfg = node.set_node_cfg('node-cfg.toml')
common_cfg = common.set_common_cfg('common-cfg.toml')

roots = []

for seq_name in node_cfg.cases.seqs:
    # Anchor
    tcopy = CopyTask(seq_name=seq_name, frames=node_cfg.frames)
    task1 = RenderTask().with_parent(tcopy)

    # W/O MCA
    task1 = Png2yuvTask().with_parent(tcopy)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.woMCA[seq_name]:
            task2 = CodecTask(vtm_type=vtm_type, QP=qp).with_parent(task1)
            task3 = Yuv2pngTask().with_parent(task2)
            task4 = RenderTask().with_parent(task3)

    # W MCA
    task1 = PreprocTask(frames=node_cfg.frames, parent=tcopy)
    task2 = Png2yuvTask(frames=node_cfg.frames, parent=task1)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.wMCA[seq_name]:
            task3 = CodecTask(vtm_type=vtm_type, frames=node_cfg.frames, QP=qp, parent=task2)
            task4 = Yuv2pngTask(parent=task3)
            task5 = PostprocTask(frames=node_cfg.frames, parent=task4)
            task6 = RenderTask(frames=node_cfg.frames, parent=task5)

    roots.append(tcopy)

if __name__ == "__main__":
    executor = Executor(roots, process_num=1)
    executor.run()
