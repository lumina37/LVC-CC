from mcahelper.config import set_common_cfg, set_node_cfg
from mcahelper.task import CodecTask, RenderTask, get_codec_task, is_anchor, tasks

node_cfg = set_node_cfg('cfg-node.toml')
common_cfg = set_common_cfg('cfg-common.toml')


def qp_filter(task: RenderTask):
    if task.seq_name == "Tunnel_Train" and is_anchor(task):
        return True
    return False


for task in tasks(RenderTask, qp_filter):
    print(f'"{task.dstdir}" is the dstdir of Task {task}')

    ctask = get_codec_task(task)
    if ctask.qp != CodecTask.DEFAULT_QP:
        codec_dstdir = ctask.dstdir
        print(f'"{codec_dstdir}" is the dstdir of {ctask}')

    print(f"Task Info: {task.taskinfo_str}")
