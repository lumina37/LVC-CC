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
    task_cnt: int = dcs.field(init=False, default=0)
    task_cnt_lock: threading.Lock = dcs.field(init=False, default_factory=threading.Lock)
    cond: threading.Condition = dcs.field(init=False, default_factory=threading.Condition)

    def _exit_ready(self) -> bool:
        """
        Check if the executor is ready for exit.

        Returns:
            bool: True if there is absolutely no more task and the executor is ready for exit, \
            False if there might have some tasks to do and the executor is not ready for exit.
        """

        with self.task_cnt_lock:
            if self.task_cnt == 0:
                return True

        return False

    def _worker(self):
        while 1:
            try:
                task: TRetTask = self.task_queue.get(block=False)

            except queue.Empty:  # noqa: PERF203
                if self._exit_ready():
                    return
                with self.cond:
                    self.cond.wait()

            else:
                with self.task_cnt_lock:
                    self.task_cnt += len(task.children)

                task.run()

                if task.children:
                    for child in task.children:
                        self.task_queue.put(child, block=False)
                    with self.cond:
                        self.cond.notify(len(task.children))

                with self.task_cnt_lock:
                    self.task_cnt -= 1

                if self._exit_ready():
                    with self.cond:
                        self.cond.notify_all()

    def run(self) -> None:
        if self.process_num < 1:
            return

        roots_dedup_map = {}
        for t in self.root_tasks:
            roots_dedup_map[t.hash] = t
        roots = list(roots_dedup_map.values())

        for root in roots:
            self.task_queue.put(root)
        self.task_cnt = len(roots)

        workers = [threading.Thread(target=self._worker) for _ in range(self.process_num)]

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()
