from lvccc.config import set_config
from lvccc.task import CodecTask, RenderTask, get_codec_task, is_anchor, tasks

set_config('config.toml')


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
