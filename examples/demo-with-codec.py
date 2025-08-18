from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import ConvertTask, CopyTask, DecodeTask, EncodeTask

update_config("base.toml")

tcopy = CopyTask(seq_name="Fujita2")
tenc = EncodeTask(qp=54).follow(tcopy)
tdec = DecodeTask().follow(tenc)
tconvert = ConvertTask(views=3).follow(tdec)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
