from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, CopyTask, Png2yuvTask, RenderTask, Yuv2pngTask

update_config('config.toml')

tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
task1 = Png2yuvTask().with_parent(tcopy)
task2 = CodecTask(qp=46).with_parent(task1)
task3 = Yuv2pngTask().with_parent(task2)
task4 = RenderTask().with_parent(task3)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
