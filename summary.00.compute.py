import json
from pathlib import Path

import cv2 as cv
import numpy as np

from lvccc.config import update_config
from lvccc.logging import get_logger
from lvccc.task import (
    CodecTask,
    ComposeTask,
    CopyTask,
    Png2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2pngTask,
)
from lvccc.task.infomap import query
from lvccc.utils import compute_psnr_yuv, get_first_file, mkdir, read_enclog

config = update_config('config.toml')

log = get_logger()

summary_dir = config.path.output / 'summary/compute'
mkdir(summary_dir)

BASES: dict[str, Path] = {}


def get_wh(task: ComposeTask) -> tuple[int, int]:
    render_dir = query(task.parent) / 'img'
    frame_dir = next(render_dir.glob('frame#*'))
    img_ref_p = get_first_file(frame_dir)
    img_ref = cv.imread(str(img_ref_p))
    height, width = img_ref.shape[:2]
    return (height, width)


def compute_psnr_task(task: RenderTask, base: ComposeTask) -> np.ndarray:
    basedir = query(base) / "yuv"
    yuvdir = query(task) / "yuv"

    width, height = get_wh(task)

    channels = 3
    accpsnr = np.zeros(channels)

    count = 0
    for lhs, rhs in zip(basedir.iterdir(), yuvdir.iterdir(), strict=True):
        accpsnr += compute_psnr_yuv(lhs, rhs, width, height)
        count += 1
    accpsnr /= count

    return accpsnr


for seq_name in config.cases.seqs:
    seq_dic = {}

    # Anchor
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    task1 = RenderTask().with_parent(tcopy)
    tbase = ComposeTask().with_parent(task1)

    # W/O MCA
    task1 = Png2yuvTask().with_parent(tcopy)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.woMCA[seq_name]:
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(task1)
            task3 = Yuv2pngTask().with_parent(tcodec)
            task4 = RenderTask().with_parent(task3)
            tcomp = ComposeTask().with_parent(task4)

            log.info(f"Handling {tcomp}")

            pre_type_dic: dict = seq_dic.setdefault('woMCA', {})
            vtm_list: list = pre_type_dic.setdefault(vtm_type, [])
            log_path = query(tcodec) / "out.log"
            enclog = read_enclog(log_path)
            psnr = compute_psnr_task(tcomp, tbase)
            vtm_list.append(
                {
                    'bitrate': enclog.bitrate,
                    'qp': qp,
                    'ypsnr': psnr[0],
                    'upsnr': psnr[1],
                    'vpsnr': psnr[2],
                }
            )

    # W MCA
    task1 = PreprocTask().with_parent(tcopy)
    task2 = Png2yuvTask().with_parent(task1)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.wMCA[seq_name]:
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(task2)
            task4 = Yuv2pngTask().with_parent(tcodec)
            task5 = PostprocTask().with_parent(task4)
            task6 = RenderTask().with_parent(task5)
            tcomp = ComposeTask().with_parent(task6)

            log.info(f"Handling {tcomp}")

            pre_type_dic: dict = seq_dic.setdefault('wMCA', {})
            vtm_list: list = pre_type_dic.setdefault(vtm_type, [])
            log_path = query(tcodec) / "out.log"
            enclog = read_enclog(log_path)
            psnr = compute_psnr_task(tcomp, tbase)
            vtm_list.append(
                {
                    'bitrate': enclog.bitrate,
                    'qp': qp,
                    'ypsnr': psnr[0],
                    'upsnr': psnr[1],
                    'vpsnr': psnr[2],
                }
            )

    with (summary_dir / f'{seq_name}.json').open('w') as f:
        json.dump(seq_dic, f, indent=2)
