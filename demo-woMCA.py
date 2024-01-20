from mcahelper.cfg import node
from mcahelper.task import CodecTask, Png2yuvTask, RenderTask, Yuv2pngTask

node.set_node_cfg('node-cfg.toml')

task1 = Png2yuvTask(seq_name="Tunnel_Train", frames=1)
task2 = CodecTask(vtm_type='AI', frames=1, QP=46, pretask=task1)
task3 = Yuv2pngTask(pretask=task2)
task4 = RenderTask(frames=1, pretask=task3)

# task1.run()
# task2.run()
# task3.run()
task4.run()
