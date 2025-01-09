from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ConvertTask, CopyTask, PostprocTask, PreprocTask

update_config("config.toml")

tcopy = CopyTask(seq_name="NagoyaFujita")
tpre = PreprocTask().with_parent(tcopy)
tcodec = CodecTask(qp=46).with_parent(tpre)
tpost = PostprocTask().with_parent(tcodec)
tconvert = ConvertTask(views=3).with_parent(tpost)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
