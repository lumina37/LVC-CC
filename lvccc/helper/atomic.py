from __future__ import annotations

import dataclasses as dcs
import threading
from typing import Self


@dcs.dataclass
class Atomic[TVal]:
    val: TVal = dcs.field(default_factory=TVal)
    lock: threading.Lock = dcs.field(init=False, default_factory=threading.Lock)

    def __enter__(self) -> Self:
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.lock.release()

    def __iadd__(self, rhs: TVal) -> Self:
        with self.lock:
            self.val += rhs
        return self

    def __isub__(self, rhs: TVal) -> Self:
        with self.lock:
            self.val += rhs
        return self

    def is_null(self) -> bool:
        with self.lock:
            return not bool(self.val)
