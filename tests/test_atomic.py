import threading

from lvccc.helper import Atomic


def test_tasks():
    atomic = Atomic(0)
    addup_per_thread = 50000
    thread_num = 4

    def addup():
        nonlocal atomic
        for _ in range(addup_per_thread):
            atomic += 1

    threads = [threading.Thread(target=addup) for _ in range(thread_num)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert atomic.val == thread_num * addup_per_thread
