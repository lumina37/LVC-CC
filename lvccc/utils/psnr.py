import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from ..config import get_config
from ..helper import get_any_file, run_cmds, size_from_filename
from ..task import CodecTask, RenderTask, TVarTask, Yuv2imgTask
from ..task.infomap import query
from .backtrack import get_ancestor
from .read_log import read_psnrlog


def calc_yuv_psnr(lhs: Path, rhs: Path, width: int, height: int) -> np.ndarray:
    with tempfile.TemporaryFile('w+') as tf:
        config = get_config()
        cmds = [
            config.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "yuv420p",
            "-i",
            lhs,
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "yuv420p",
            "-i",
            rhs,
            "-lavfi",
            "psnr",
            "-f",
            "null",
            "-",
        ]
        run_cmds(cmds, output=tf)

        tf.seek(0)
        psnr = read_psnrlog(tf)

    psnrarr = np.asarray([psnr.y, psnr.u, psnr.v])
    return psnrarr


def calc_mv_psnr(task: RenderTask) -> np.ndarray:
    copy_task = task.chain[0]
    render_task = RenderTask(views=task.views).with_parent(copy_task)

    base_dir = query(render_task) / "yuv"
    self_dir = query(task) / "yuv"

    width, height = size_from_filename(get_any_file(base_dir, '*.yuv').name)

    channels = 3
    accpsnr = np.zeros(channels)

    lhss = sorted(base_dir.iterdir())
    rhss = sorted(self_dir.iterdir())
    count = len(lhss)

    for lhs, rhs in zip(lhss, rhss, strict=True):
        accpsnr += calc_yuv_psnr(lhs, rhs, width, height)
    accpsnr /= count

    return accpsnr


def calc_lenslet_psnr(task: RenderTask) -> np.ndarray:
    copy_task = task.chain[0]
    codec_task = get_ancestor(task, CodecTask)

    lhs = get_any_file(query(copy_task), '*.yuv')
    rhs = get_any_file(query(codec_task), '*.yuv')

    width, height = size_from_filename(lhs.name)

    psnr = calc_yuv_psnr(lhs, rhs, width, height)
    return psnr
