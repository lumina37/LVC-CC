from mcahelper.config import set_common_cfg, set_node_cfg
from mcahelper.executor import Executor
from mcahelper.task import CodecTask, CopyTask, Png2yuvTask, RenderTask, Yuv2pngTask

set_common_cfg('cfg-common.toml')
set_node_cfg('cfg-node.toml')

tcopy = CopyTask(seq_name="Tunnel_Train", frames=1)
task1 = Png2yuvTask().with_parent(tcopy)
task2 = CodecTask(vtm_type='AI', QP=46).with_parent(task1)
task3 = Yuv2pngTask().with_parent(task2)
task4 = RenderTask().with_parent(task3)

if __name__ == "__main__":
    executor = Executor([tcopy], process_num=1)
    executor.run()
