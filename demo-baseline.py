from mcahelper.config import set_common_cfg, set_node_cfg
from mcahelper.executor import Executor
from mcahelper.task import CopyTask, RenderTask

set_common_cfg('cfg-common.toml')
set_node_cfg('cfg-node.toml')

tcopy = CopyTask(seq_name="Tunnel_Train", frames=1)
trender = RenderTask().with_parent(tcopy)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
