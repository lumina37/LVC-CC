from pathlib import Path

import cv2 as cv

from mcahelper.config import node
from mcahelper.logging import get_logger
from mcahelper.task import RenderTask, iterator
from mcahelper.task.infomap import query
from mcahelper.utils import get_first_file, mkdir, run_cmds

node_cfg = node.set_node_cfg('node-cfg.toml')

log = get_logger()


BASES: dict[str, Path] = {}


def compose(task: RenderTask):
    basedir = query(task)
    dstdir = basedir / "yuv"
    mkdir(dstdir)

    view_idx = 1
    for row_idx in range(1, task.views + 1):
        for col_idx in range(1, task.views + 1):
            cmds = [
                node_cfg.app.ffmpeg,
                "-i",
                basedir / "img" / "frame#%03d" / f"image_{view_idx:0>3}.png",
                "-vf",
                "format=yuv420p",
                "-frames:v",
                task.frames,
                dstdir / f"{row_idx}-{col_idx}.yuv",
                "-v",
                "warning",
                "-y",
            ]
            run_cmds(cmds)

            view_idx += 1


def get_wh(task: RenderTask) -> tuple[int, int]:
    render_dir = query(task) / 'img'
    frame_dir = next(render_dir.glob('frame#*'))
    img_ref_p = get_first_file(frame_dir)
    img_ref = cv.imread(str(img_ref_p))
    height, width = img_ref.shape[:2]
    return (height, width)


for task in iterator.tasks(RenderTask):
    if task.frames != node_cfg.frames:
        continue
    if task.seq_name not in node_cfg.cases.seqs:
        continue

    log.info(f"Handling {task}")
    compose(task)
