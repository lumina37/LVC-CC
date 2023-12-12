from mcahelper.cfg import node
from mcahelper.task import Png2yuvTask, PreprocTask

node.set_node_cfg('node-cfg.toml')

task1 = PreprocTask(seq_name="Tunnel_Train")
task2 = Png2yuvTask(seq_name="Tunnel_Train", pretask=task1, frames=1)

# task1.run()
# task2.run()
