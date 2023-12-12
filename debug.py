from mcahelper.cfg import node
from mcahelper.task.png2yuv import Png2yuvTask
from mcahelper.task.preproc import PreprocTask

node.set_node_cfg('node-cfg.toml')

preproc_task = PreprocTask(seq_name="Tunnel_Train")
task = Png2yuvTask(seq_name="Tunnel_Train", pretask=preproc_task, frames=30)
#preproc_task.run()
task.run()
