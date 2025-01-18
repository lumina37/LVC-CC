import threading

from lvccc.helper import ThreadAtomic


def test_tasks():
    val = ThreadAtomic(0)
    addup_per_thread = 50000
    thread_num = 4

    def addup():
        nonlocal val
        for _ in range(addup_per_thread):
            val += 1

    threads = [threading.Thread(target=addup) for _ in range(thread_num)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert val.val == thread_num * addup_per_thread
