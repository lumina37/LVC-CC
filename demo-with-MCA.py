from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ConvertTask, CopyTask, PostprocTask, PreprocTask

update_config("config.toml")

tcopy = CopyTask(seq_name="Fujita2")
tpre = PreprocTask().follow(tcopy)
tcodec = CodecTask(qp=46).follow(tpre)
tpost = PostprocTask().follow(tcodec)
tconvert = ConvertTask(views=3).follow(tpost)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
