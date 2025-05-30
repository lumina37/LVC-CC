from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import ConvertTask, CopyTask

update_config("base.toml")

tcopy = CopyTask(seq_name="Fujita2")
tconvert = ConvertTask(views=3).follow(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
