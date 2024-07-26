from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, CopyTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

update_config('config.toml')

tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
tpre = PreprocTask().with_parent(tcopy)
tp2y = Png2yuvTask().with_parent(tpre)
tcodec = CodecTask(qp=46).with_parent(tp2y)
ty2p = Yuv2pngTask().with_parent(tcodec)
tpost = PostprocTask().with_parent(ty2p)
trender = RenderTask().with_parent(tpost)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
