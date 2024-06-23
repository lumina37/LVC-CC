from mcahelper.config import node
from mcahelper.executor import Executor
from mcahelper.task import RLCRenderTask

node.set_node_cfg('node-cfg.toml')

task = RLCRenderTask(seq_name="Tunnel_Train", frames=1)

if __name__ == "__main__":
    executor = Executor([task], process_num=1)
    executor.run()
