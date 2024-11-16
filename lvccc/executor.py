import dataclasses as dcs
import queue
import threading

from .task.abc import TRetTask
from .task.infomap import TypeInfomap, get_infomap


@dcs.dataclass
class Executor:
    root_tasks: list[TRetTask]
    process_num: int = 1

    infomap: TypeInfomap = dcs.field(init=False, default_factory=get_infomap)
    task_queue: queue.Queue = dcs.field(init=False, default_factory=queue.Queue)
    active_count: int = dcs.field(init=False, default=0)
    active_count_lock: threading.Lock = dcs.field(init=False, default_factory=threading.Lock)
    pending_count: int = dcs.field(init=False, default=0)
    pending_count_lock: threading.Lock = dcs.field(init=False, default_factory=threading.Lock)
    waitfor_task_cond: threading.Condition = dcs.field(init=False, default_factory=threading.Condition)

    def _exit_ready(self) -> bool:
        """
        Check if the executor is ready for exit.

        Returns:
            bool: True if there is absolutely no more task and the executor is ready for exit, \
            False if there might have some tasks to do and the executor is not ready for exit.
        """

        zero_count = 0

        with self.active_count_lock:
            if self.active_count == 0:
                zero_count += 1

        with self.pending_count_lock:
            if self.pending_count == 0:
                zero_count += 1

        exit_allowed = zero_count == 2
        return exit_allowed

    def _worker(self):
        while 1:
            try:
                task: TRetTask = self.task_queue.get(block=False)

            except queue.Empty:  # noqa: PERF203
                if self._exit_ready():
                    return
                with self.waitfor_task_cond:
                    self.waitfor_task_cond.wait()

            else:
                with self.active_count_lock:
                    self.active_count += 1
                with self.pending_count_lock:
                    self.pending_count += len(task.children)
                    self.pending_count -= 1

                task.run()

                if task.children:
                    for child in task.children:
                        self.task_queue.put(child, block=False)
                    with self.waitfor_task_cond:
                        self.waitfor_task_cond.notify(len(task.children))

                with self.active_count_lock:
                    self.active_count -= 1

                if self._exit_ready():
                    with self.waitfor_task_cond:
                        self.waitfor_task_cond.notify_all()

    def run(self) -> None:
        if self.process_num < 1:
            return

        roots_dedup_map = {}
        for t in self.root_tasks:
            roots_dedup_map[t.hash] = t
        roots = list(roots_dedup_map.values())

        for root in roots:
            self.task_queue.put(root)
        self.pending_count = len(roots)

        workers = [threading.Thread(target=self._worker) for _ in range(self.process_num)]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()
