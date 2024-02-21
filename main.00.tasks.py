import multiprocessing as mp

import tomllib

from mcahelper.cfg import node
from mcahelper.task import CodecTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask
from mcahelper.task.base import BaseTask

node_cfg = node.set_node_cfg('node-cfg.toml')


FRAMES = 1

with open('QP.toml', 'rb') as f:
    QPs = tomllib.load(f)


def run(task: BaseTask) -> None:
    task.run()


def task_generator():
    for seq_name in node_cfg.cases.seqs:
        task = RenderTask(seq_name=seq_name, frames=FRAMES)
        yield task

    for seq_name in node_cfg.cases.seqs:
        for vtm_type in node_cfg.cases.vtm_types:
            task1 = Png2yuvTask(seq_name=seq_name, frames=1)
            yield task1

            for qp in QPs['woMCA'][seq_name]:
                task2 = CodecTask(vtm_type=vtm_type, frames=FRAMES, QP=qp, parent=task1)
                yield task2
                task3 = Yuv2pngTask(parent=task2)
                yield task3
                task4 = RenderTask(frames=FRAMES, parent=task3)
                yield task4

    for seq_name in node_cfg.cases.seqs:
        for vtm_type in node_cfg.cases.vtm_types:
            task1 = PreprocTask(seq_name=seq_name)
            yield task1
            task2 = Png2yuvTask(frames=FRAMES, parent=task1)
            yield task2

            for qp in QPs['wMCA'][seq_name]:
                task3 = CodecTask(vtm_type=vtm_type, frames=FRAMES, QP=qp, parent=task2)
                yield task3
                task4 = Yuv2pngTask(parent=task3)
                yield task4
                task5 = PostprocTask(parent=task4)
                yield task5
                task6 = RenderTask(frames=FRAMES, parent=task5)
                yield task6


if __name__ == "__main__":
    with mp.Pool(processes=3) as pool:
        pool.map_async(run, task_generator())
        pool.close()
        pool.join()
