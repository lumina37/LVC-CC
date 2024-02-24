import dataclasses as dcs
import multiprocessing as mp

from .task import BaseTask
from .task.infomap import TypeInfomap, init_infomap, register_infomap


@dcs.dataclass
class Executor:

    anytasks: list[BaseTask]
    process_num: int = 2

    @staticmethod
    def find_root(task: BaseTask) -> BaseTask:
        while task.parent is not None:
            task = task.parent
        return task

    @staticmethod
    def _worker(queue: mp.Queue, active_count: mp.Value, infomap: TypeInfomap):
        register_infomap(infomap)

        while 1:
            task: BaseTask = queue.get()

            # Active before actually run
            with active_count.get_lock():
                active_count.value += 1

            task.run()

            with active_count.get_lock():
                active_count.value -= 1

            if task.children:
                for child in task.children:
                    queue.put(child)

            elif active_count.value == 0 and queue.empty():
                # Quit if there is no more tasks and no active worker
                # Note that queue.empty() has a sightly delay
                queue.close()
                break

    def run(self) -> None:
        roots = {}
        for t in self.anytasks:
            roots[t.hash] = t

        queue = mp.Queue()
        for root in roots.values():
            queue.put(root)
        active_count = mp.Value('Q', 0)
        manager = mp.Manager()
        infomap = manager.dict()
        infomap.update(init_infomap())

        workers: list[mp.Process] = []
        for _ in range(self.process_num):
            worker = mp.Process(target=self._worker, args=(queue, active_count, infomap))
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()
