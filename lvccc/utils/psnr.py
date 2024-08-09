import tempfile
from pathlib import Path

import cv2 as cv
import numpy as np

from ..config import get_config
from ..helper import get_first_file, run_cmds, size_from_filename
from ..task import CodecTask, ComposeTask, RenderTask, TVarTask, Yuv2pngTask
from ..task.infomap import query
from .backtrack import get_ancestor
from .read_log import read_psnrlog


def calc_yuv_psnr(lhs: Path, rhs: Path, width: int, height: int) -> np.ndarray:
    with tempfile.NamedTemporaryFile('w', delete_on_close=False) as tf:
        tf.close()

        config = get_config()
        temp_path = Path(tf.name)
        temp_path_str = str(temp_path).replace('\\', '/').replace(':', '\\:')
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
            f"psnr=stats_file='{temp_path_str}'",
            "-v",
            "warning",
            "-f",
            "null",
            "-",
        ]
        run_cmds(cmds)

        psnr = read_psnrlog(temp_path)

    psnrarr = np.asarray([psnr.y, psnr.u, psnr.v])
    return psnrarr


def get_render_wh(task: TVarTask) -> tuple[int, int]:
    render_task = get_ancestor(task, RenderTask)
    render_dir = query(render_task) / 'img'
    frame_dir = next(render_dir.glob('frame#*'))
    img_ref_p = get_first_file(frame_dir)
    img_ref = cv.imread(str(img_ref_p))
    height, width = img_ref.shape[:2]
    return width, height


def calc_mv_psnr(task: ComposeTask) -> np.ndarray:
    copy_task = task.chain[0]
    views = task.parent.views

    yuv2png_task = Yuv2pngTask().with_parent(copy_task)
    render_task = RenderTask(views=views).with_parent(yuv2png_task)
    compose_task = ComposeTask().with_parent(render_task)

    base_dir = query(compose_task) / "yuv"
    self_dir = query(task) / "yuv"

    width, height = get_render_wh(task)

    channels = 3
    accpsnr = np.zeros(channels)

    count = 0
    for lhs, rhs in zip(base_dir.iterdir(), self_dir.iterdir(), strict=True):
        accpsnr += calc_yuv_psnr(lhs, rhs, width, height)
        count += 1
    accpsnr /= count

    return accpsnr


def calc_lenslet_psnr(task: ComposeTask) -> np.ndarray:
    copy_task = task.chain[0]
    codec_task = get_ancestor(task, CodecTask)
    lhs = next(query(copy_task).glob('*.yuv'))
    rhs = next(query(codec_task).glob('*.yuv'))

    width, height = size_from_filename(lhs.name)

    psnr = calc_yuv_psnr(lhs, rhs, width, height)
    return psnr
