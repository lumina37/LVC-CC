import dataclasses as dcs
import multiprocessing as mp

from .task import BaseTask


@dcs.dataclass
class Executer:

    anytasks: list[BaseTask]
    process_num: int = 2

    @staticmethod
    def find_root(task: BaseTask) -> BaseTask:
        while task.parent is not None:
            task = task.parent
        return task

    @staticmethod
    def _worker(queue: mp.Queue, active_count: mp.Value):
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
            else:
                # Quit if there is no more tasks and no active worker
                if active_count.value == 0:
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

        workers: list[mp.Process] = []
        for _ in range(self.process_num):
            worker = mp.Process(target=self._worker, args=(queue, active_count))
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()
