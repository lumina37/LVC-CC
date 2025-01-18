from __future__ import annotations

import dataclasses as dcs
import threading


@dcs.dataclass
class ThreadAtomic[T]:
    val: T = dcs.field(default_factory=T)
    lock: threading.Lock = dcs.field(init=False, default_factory=threading.Lock)

    def __bool__(self) -> bool:
        with self.lock:
            return bool(self.val)

    def __iadd__(self, rhs: T | ThreadAtomic[T]) -> ThreadAtomic:
        if isinstance(rhs, ThreadAtomic):
            with self.lock:
                self.val += rhs.val
        else:
            with self.lock:
                self.val += rhs
        return self

    def __isub__(self, rhs: T | ThreadAtomic[T]) -> ThreadAtomic:
        if isinstance(rhs, ThreadAtomic):
            with self.lock:
                self.val -= rhs.val
        else:
            with self.lock:
                self.val -= rhs
        return self
