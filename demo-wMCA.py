from mcahelper.cfg import node
from mcahelper.task import CodecTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask

node.set_node_cfg('node-cfg.toml')

task1 = PreprocTask(seq_name="Tunnel_Train")
task2 = Png2yuvTask(frames=1, parent=task1)
task3 = CodecTask(vtm_type='AI', frames=1, QP=46, parent=task2)
task4 = Yuv2pngTask(parent=task3)
task5 = PostprocTask(parent=task4)
task6 = RenderTask(frames=1, parent=task5)

task1.run()
task2.run()
task3.run()
task4.run()
task5.run()
task6.run()
