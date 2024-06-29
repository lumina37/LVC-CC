from mcahelper.config import set_common_cfg, set_node_cfg
from mcahelper.task import RenderTask, get_codec_task, tasks

node_cfg = set_node_cfg('cfg-node.toml')
common_cfg = set_common_cfg('cfg-common.toml')


def qp_filter(task: RenderTask):
    return get_codec_task(task).QP != 0


for task in tasks(RenderTask, qp_filter):
    print(task.dstdir)
    print(task.taskinfo_str)
