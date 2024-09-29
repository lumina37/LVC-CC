from lvccc.config import update_config
from lvccc.executor import Executor
from lvccc.task import ImgCopyTask, RenderTask

update_config('config.toml')

tcopy = ImgCopyTask(seq_name="NagoyaFujita")
trender = RenderTask().with_parent(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy])
    executor.run()
