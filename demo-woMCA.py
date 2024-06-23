from mcahelper.config import node
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, Png2yuvTask, RLCRenderTask, Yuv2pngTask

node.set_node_cfg('node-cfg.toml')

task1 = Png2yuvTask(seq_name="Tunnel_Train", frames=1)
task2 = CodecTask(vtm_type='AI', frames=1, QP=46, parent=task1)
task3 = Yuv2pngTask(parent=task2)
task4 = RLCRenderTask(frames=1, parent=task3)

if __name__ == "__main__":
    executor = Executor([task1], process_num=1)
    executor.run()
