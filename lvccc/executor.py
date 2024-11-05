import dataclasses as dcs
import queue
import threading

from .task.abc import TRetTask
from .task.infomap import TypeInfomap, get_infomap


@dcs.dataclass
class Executor:
    root_tasks: list[TRetTask]
    process_num: int = 1

    infomap: TypeInfomap = dcs.field(default_factory=get_infomap)
    task_queue: queue.Queue = dcs.field(default_factory=queue.Queue)
    active_count: int = 0
    active_count_lock: threading.Lock = dcs.field(default_factory=threading.Lock)

    def _worker(self):
        while 1:
            try:
                task: TRetTask = self.task_queue.get(block=False)

            except queue.Empty:  # noqa: PERF203
                with self.active_count_lock:
                    if self.active_count == 0:
                        break

            else:
                with self.active_count_lock:
                    self.active_count += 1

                task.run()

                with self.active_count_lock:
                    self.active_count -= 1

                    if task.children:
                        for child in task.children:
                            self.task_queue.put(child)

    def run(self) -> None:
        if self.process_num < 1:
            return

        roots = {}
        for t in self.root_tasks:
            roots[t.hash] = t

        for root in roots.values():
            self.task_queue.put(root)

        workers: list[threading.Thread] = []
        for _ in range(self.process_num):
            worker = threading.Thread(target=self._worker)
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()
