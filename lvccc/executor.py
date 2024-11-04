import ctypes
import dataclasses as dcs
import multiprocessing as mp
import queue

from .task.abc import TRetTask
from .task.infomap import TypeInfomap, get_infomap, register_infomap


@dcs.dataclass
class Executor:
    root_tasks: list[TRetTask]
    process_num: int = 1

    @staticmethod
    def _worker(que: mp.Queue, active_count, infomap: TypeInfomap):
        register_infomap(infomap)

        while 1:
            try:
                task: TRetTask = que.get(timeout=1.0)

            except queue.Empty:  # noqa: PERF203
                if active_count.value == 0 and que.empty():
                    break

            else:
                with active_count.get_lock():
                    active_count.value += 1

                task.run()

                with active_count.get_lock():
                    active_count.value -= 1

                if task.children:
                    for child in task.children:
                        que.put(child)

    def run(self) -> None:
        roots = {}
        for t in self.root_tasks:
            roots[t.hash] = t

        queue = mp.Queue()
        for root in roots.values():
            queue.put(root)
        active_count = mp.Value(ctypes.c_size_t, 0)
        manager = mp.Manager()
        infomap = manager.dict()
        infomap.update(get_infomap())

        workers: list[mp.Process] = []
        for _ in range(self.process_num):
            worker = mp.Process(target=self._worker, args=(queue, active_count, infomap))
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()
