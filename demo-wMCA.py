from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Img2yuvTask, ImgCopyTask, PostprocTask, PreprocTask, RenderTask, Yuv2imgTask

update_config('config.toml')

tcopy = ImgCopyTask(seq_name="NagoyaFujita")
tpre = PreprocTask().with_parent(tcopy)
ti2y = Img2yuvTask().with_parent(tpre)
tcodec = CodecTask(qp=46).with_parent(ti2y)
ty2i = Yuv2imgTask().with_parent(tcodec)
tpost = PostprocTask().with_parent(ty2i)
trender = RenderTask().with_parent(tpost)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
