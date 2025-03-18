from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CodecTask, ConvertTask, CopyTask

update_config("base.toml")

tcopy = CopyTask(seq_name="Fujita2")
tcodec = CodecTask(qp=54).follow(tcopy)
tconvert = ConvertTask(views=3).follow(tcodec)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
