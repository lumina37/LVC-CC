from mcahelper.config import node
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, Png2yuvTask, PostprocTask, PreprocTask, RLCRenderTask, Yuv2pngTask

node.set_node_cfg('node-cfg.toml')

seq_name = "Tunnel_Train"
task1 = PreprocTask(seq_name=seq_name)
task2 = Png2yuvTask(frames=1, parent=task1)
task3 = CodecTask(vtm_type='AI', frames=1, QP=46, parent=task2)
task4 = Yuv2pngTask(parent=task3)
task5 = PostprocTask(parent=task4)
task6 = RLCRenderTask(frames=1, parent=task5)

if __name__ == "__main__":
    executor = Executor([task1], process_num=1)
    executor.run()
