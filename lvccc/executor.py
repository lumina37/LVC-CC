from __future__ import annotations

import dataclasses as dcs
import queue
import threading
from typing import TYPE_CHECKING

from .helper import Atomic
from .task.infomap import TypeInfomap, get_infomap

if TYPE_CHECKING:
    from .task.abc import ProtoTask


@dcs.dataclass
class Executor:
    root_tasks: list[ProtoTask]
    process_num: int = 1

    infomap: TypeInfomap = dcs.field(init=False, default_factory=get_infomap)
    task_queue: queue.Queue = dcs.field(init=False, default_factory=queue.Queue)
    task_cnt: Atomic[int] = dcs.field(init=False, default_factory=lambda: Atomic(0))
    cond: threading.Condition = dcs.field(init=False, default_factory=threading.Condition)

    def _worker(self):
        while 1:
            try:
                task: ProtoTask = self.task_queue.get(block=False)

            except queue.Empty:  # noqa: PERF203
                if self.task_cnt.is_null():
                    return
                with self.cond:
                    self.cond.wait()

            else:
                children_cnt = len(task.children)
                self.task_cnt += children_cnt
                task.run()

                if task.children:
                    for child in task.children:
                        self.task_queue.put(child, block=False)
                    with self.cond:
                        self.cond.notify(children_cnt)

                self.task_cnt -= 1

                if self.task_cnt.is_null():
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
        self.task_cnt.val = len(roots)

        workers = [threading.Thread(target=self._worker) for _ in range(self.process_num)]
        for worker in workers:
            worker.start()
            worker.join()
