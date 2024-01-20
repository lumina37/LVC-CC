from mcahelper.cfg import node
from mcahelper.task import RenderTask

node.set_node_cfg('node-cfg.toml')

task = RenderTask(seq_name="Tunnel_Train", frames=1)

task.run()
