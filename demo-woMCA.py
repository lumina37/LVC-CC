from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, Img2yuvTask, ImgCopyTask, RenderTask, Yuv2imgTask

update_config('config.toml')

tcopy = ImgCopyTask(seq_name="NagoyaFujita", frames=1)
ti2y = Img2yuvTask().with_parent(tcopy)
tcodec = CodecTask(qp=46).with_parent(ti2y)
ty2i = Yuv2imgTask().with_parent(tcodec)
trender = RenderTask().with_parent(ty2i)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
