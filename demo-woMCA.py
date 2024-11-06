from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, RenderTask, YuvCopyTask

update_config('config.toml')

tcopy = YuvCopyTask(seq_name="NagoyaFujita")
tcodec = CodecTask(qp=46).with_parent(tcopy)
trender = RenderTask().with_parent(tcodec)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
