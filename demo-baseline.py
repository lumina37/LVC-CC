from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import ConvertTask, CopyTask

update_config("config.toml")

tcopy = CopyTask(seq_name="NagoyaFujita")
tconvert = ConvertTask(views=3).with_parent(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
