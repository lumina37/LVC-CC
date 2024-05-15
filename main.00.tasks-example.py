from mcahelper.cfg import common, node
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

node_cfg = node.set_node_cfg('node-cfg.toml')
common_cfg = common.set_common_cfg('common-cfg.toml')

roots = []

for seq_name in node_cfg.cases.seqs:
    task = RenderTask(seq_name=seq_name, frames=node_cfg.frames)
    roots.append(task)

for seq_name in node_cfg.cases.seqs:
    task1 = Png2yuvTask(seq_name=seq_name, frames=node_cfg.frames)
    roots.append(task1)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.woMCA[seq_name]:
            task2 = CodecTask(vtm_type=vtm_type, frames=node_cfg.frames, QP=qp, parent=task1)
            task3 = Yuv2pngTask(parent=task2)
            task4 = RenderTask(frames=node_cfg.frames, parent=task3)

for seq_name in node_cfg.cases.seqs:
    task1 = PreprocTask(seq_name=seq_name)
    roots.append(task1)
    task2 = Png2yuvTask(frames=node_cfg.frames, parent=task1)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.wMCA[seq_name]:
            task3 = CodecTask(vtm_type=vtm_type, frames=node_cfg.frames, QP=qp, parent=task2)
            task4 = Yuv2pngTask(parent=task3)
            task5 = PostprocTask(parent=task4)
            task6 = RenderTask(frames=node_cfg.frames, parent=task5)


if __name__ == "__main__":
    executor = Executor(roots, process_num=4)
    executor.run()
