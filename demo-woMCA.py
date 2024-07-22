from lvccc.config import set_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, CopyTask, Png2yuvTask, RenderTask, Yuv2pngTask

set_config('config.toml')

tcopy = CopyTask(seq_name="Tunnel_Train", frames=1)
task1 = Png2yuvTask().with_parent(tcopy)
task2 = CodecTask(vtm_type='AI', qp=46).with_parent(task1)
task3 = Yuv2pngTask().with_parent(task2)
task4 = RenderTask().with_parent(task3)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
