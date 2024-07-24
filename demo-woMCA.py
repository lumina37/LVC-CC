from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, CopyTask, Png2yuvTask, RenderTask, Yuv2pngTask

update_config('config.toml')

tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
tp2y = Png2yuvTask().with_parent(tcopy)
tcodec = CodecTask(qp=46).with_parent(tp2y)
ty2p = Yuv2pngTask().with_parent(tcodec)
trender = RenderTask().with_parent(ty2p)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
