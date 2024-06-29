from mcahelper.config import node
from mcahelper.executor import Executor
from mcahelper.task import RenderTask

node.set_node_cfg('node-cfg.toml')

task = RenderTask(seq_name="Tunnel_Train", frames=1)

if __name__ == "__main__":
    executor = Executor([task], process_num=1)
    executor.run()
