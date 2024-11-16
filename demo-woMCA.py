from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ConvertTask, YuvCopyTask

update_config('config.toml')

tcopy = YuvCopyTask(seq_name="NagoyaFujita")
tcodec = CodecTask(qp=46).with_parent(tcopy)
tconvert = ConvertTask().with_parent(tcodec)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
