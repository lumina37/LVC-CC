from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import ConvertTask, YuvCopyTask

update_config('config.toml')

tcopy = YuvCopyTask(seq_name="NagoyaFujita")
tconvert = ConvertTask().with_parent(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
