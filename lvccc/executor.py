from __future__ import annotations

import dataclasses as dcs
import queue
import threading
import time
import traceback
from typing import TYPE_CHECKING

from .helper import Atomic, mkdir
from .logging import get_logger
from .task.infomap import append, query

if TYPE_CHECKING:
    from .task.abc import ProtoTask


def run_task(task: ProtoTask) -> bool:
    if query(task):
        return True

    log = get_logger()

    try:
        mkdir(task.dstdir)
        start_ns = time.monotonic_ns()
        task.run()
        end_ns = time.monotonic_ns()
    except Exception:
        log.error(f"Task `{task.dstdir.name}` failed! Reason: {traceback.format_exc()}")
        return False
    else:
        task.dump_taskinfo(task.dstdir / "task.json")
        append(task, task.dstdir.absolute())
        elasped_s = (end_ns - start_ns) / 1e9
        log.info(f"Task `{task.dstdir.name}` completed! Elapsed time: {elasped_s:.3f}s")
        return True


@dcs.dataclass
class Executor:
    root_tasks: list[ProtoTask]
    process_num: int = 1

    task_queue: queue.Queue = dcs.field(init=False, default_factory=queue.Queue)
    task_cnt: Atomic[int] = dcs.field(init=False, default_factory=lambda: Atomic(0))
    cond: threading.Condition = dcs.field(init=False, default_factory=threading.Condition)

    def _worker(self):
        while 1:
            try:
                task: ProtoTask = self.task_queue.get(block=False)

            except queue.Empty:  # noqa: PERF203
                if not self.task_cnt:
                    return
                with self.cond:
                    self.cond.wait()

            else:
                if run_task(task):
                    if task.children:
                        for child in task.children:
                            self.task_queue.put(child, block=False)

                        children_cnt = len(task.children)
                        self.task_cnt += children_cnt

                        with self.cond:
                            self.cond.notify(children_cnt)

                self.task_cnt -= 1

                if not self.task_cnt:
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
        for worker in workers:
            worker.join()
