from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import CopyTask, RenderTask

update_config('config.toml')

tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
trender = RenderTask().with_parent(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
