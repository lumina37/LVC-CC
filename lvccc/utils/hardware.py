from __future__ import annotations

import os


def avaliable_cpu_count() -> int:
    if hasattr(os, "sched_getaffinity"):
        cnt = len(os.sched_getaffinity(0))
    else:
        cnt = os.cpu_count()
        if cnt is None:
            cnt = 1
    return cnt
