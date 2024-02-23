import tomllib

from mcahelper.cfg import node
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

node_cfg = node.set_node_cfg('node-cfg.toml')


FRAMES = 1

with open('QP.toml', 'rb') as f:
    QPs = tomllib.load(f)

roots = []

for seq_name in node_cfg.cases.seqs:
    task = RenderTask(seq_name=seq_name, frames=FRAMES)
    roots.append(task)

for seq_name in node_cfg.cases.seqs:
    task1 = Png2yuvTask(seq_name=seq_name, frames=1)
    roots.append(task1)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in QPs['woMCA'][seq_name]:
            task2 = CodecTask(seq_name=seq_name, vtm_type=vtm_type, frames=FRAMES, QP=qp, parent=task1)
            task3 = Yuv2pngTask(seq_name=seq_name, parent=task2)
            task4 = RenderTask(seq_name=seq_name, frames=FRAMES, parent=task3)

for seq_name in node_cfg.cases.seqs:
    task1 = PreprocTask(seq_name=seq_name)
    roots.append(task1)
    task2 = Png2yuvTask(seq_name=seq_name, frames=FRAMES, parent=task1)

    for vtm_type in node_cfg.cases.vtm_types:
        for qp in QPs['wMCA'][seq_name]:
            task3 = CodecTask(seq_name=seq_name, vtm_type=vtm_type, frames=FRAMES, QP=qp, parent=task2)
            task4 = Yuv2pngTask(seq_name=seq_name, parent=task3)
            task5 = PostprocTask(seq_name=seq_name, parent=task4)
            task6 = RenderTask(seq_name=seq_name, frames=FRAMES, parent=task5)


if __name__ == "__main__":
    executor = Executor(roots, process_num=2)
    executor.run()
