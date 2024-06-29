import dataclasses as dcs
import json
import re
from pathlib import Path

import cv2 as cv
import numpy as np

from mcahelper.config import common, node
from mcahelper.helper import get_first_file, mkdir
from mcahelper.logging import get_logger
from mcahelper.task import (
    CodecTask,
    ComposeTask,
    CopyTask,
    Png2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2pngTask,
)
from mcahelper.task.infomap import query

node_cfg = node.set_node_cfg('node-cfg.toml')
common_cfg = common.set_common_cfg('common-cfg.toml')

log = get_logger()

summary_dir = node_cfg.path.dataset / 'summary/compute'
mkdir(summary_dir)

BASES: dict[str, Path] = {}


@dcs.dataclass
class EncLog:
    bitrate: float
    timecost: float


def analyze_enclog(log_path: Path) -> EncLog:
    with log_path.open("r", encoding='utf-8') as f:
        layerid_row_idx = -128

        for i, row in enumerate(f):
            if row.startswith("LayerId"):
                layerid_row_idx = i

            if layerid_row_idx > 0:
                if i == layerid_row_idx + 2:
                    matchobj = re.findall(r"\d+\.?\d*", row)
                    bitrate_str = matchobj[1]
                    bitrate = float(bitrate_str)
                    continue

                if i == layerid_row_idx + 5:
                    matchobj = re.search(r"Time:\s+(\d+\.?\d*)", row)
                    timecost_str = matchobj.group(1)
                    timecost = float(timecost_str)
                    continue

    log = EncLog(bitrate, timecost)
    return log


def get_wh(task: ComposeTask) -> tuple[int, int]:
    render_dir = query(task.parent) / 'img'
    frame_dir = next(render_dir.glob('frame#*'))
    img_ref_p = get_first_file(frame_dir)
    img_ref = cv.imread(str(img_ref_p))
    height, width = img_ref.shape[:2]
    return (height, width)


def compute_psnr_array(lhs: np.ndarray, rhs: np.ndarray) -> float:
    mse = np.mean((lhs - rhs) ** 2)
    psnr = np.log10(1.0 / mse) * 10.0
    return psnr


def compute_psnr_yuv(lhs: Path, rhs: Path, frames: int, width: int, height: int) -> np.ndarray:
    lhs_size = lhs.stat().st_size
    rhs_size = rhs.stat().st_size
    assert lhs_size == rhs_size

    ysize = width * height
    uvsize = ysize // 4

    channels = 3
    psnr = np.zeros(channels)

    with lhs.open('rb', buffering=ysize) as lhs_file, rhs.open('rb', buffering=ysize) as rhs_file:
        for _ in range(frames):
            lhs_buff = lhs_file.read(ysize)
            rhs_buff = rhs_file.read(ysize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr[0] += compute_psnr_array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr[1] += compute_psnr_array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr[2] += compute_psnr_array(lhs_arr, rhs_arr)

    psnr /= frames

    return psnr


def compute_psnr_task(task: RenderTask, base: ComposeTask) -> np.ndarray:
    basedir = query(base) / "yuv"
    yuvdir = query(task) / "yuv"

    width, height = get_wh(task)

    channels = 3
    psnr = np.zeros(channels)

    count = 0
    for lhs, rhs in zip(basedir.iterdir(), yuvdir.iterdir(), strict=True):
        psnr += compute_psnr_yuv(lhs, rhs, task.frames, width, height)
        count += 1
    psnr /= count

    return psnr


for seq_name in node_cfg.cases.seqs:
    seq_dic = {}

    # Anchor
    tcopy = CopyTask(seq_name=seq_name, frames=node_cfg.frames)

    task1 = RenderTask().with_parent(tcopy)
    tbase = ComposeTask().with_parent(task1)

    # W/O MCA
    task1 = Png2yuvTask().with_parent(tcopy)
    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.woMCA[seq_name]:
            tcodec = CodecTask(vtm_type=vtm_type, QP=qp).with_parent(task1)
            task3 = Yuv2pngTask().with_parent(tcodec)
            task4 = RenderTask().with_parent(task3)
            tcomp = ComposeTask().with_parent(task4)

            log.info(f"Handling {tcomp}")

            pre_type_dic: dict = seq_dic.setdefault('woMCA', {})
            vtm_list: list = pre_type_dic.setdefault(vtm_type, [])
            log_path = query(tcodec) / "out.log"
            enclog = analyze_enclog(log_path)
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
    for vtm_type in node_cfg.cases.vtm_types:
        for qp in common_cfg.QP.wMCA[seq_name]:
            task3 = CodecTask(vtm_type=vtm_type, QP=qp).with_parent(task2)
            task4 = Yuv2pngTask().with_parent(task3)
            task5 = PostprocTask().with_parent(task4)
            task6 = RenderTask().with_parent(task5)
            task7 = ComposeTask().with_parent(task6)

            log.info(f"Handling {tcomp}")

            pre_type_dic: dict = seq_dic.setdefault('woMCA', {})
            vtm_list: list = pre_type_dic.setdefault(vtm_type, [])
            log_path = query(tcodec) / "out.log"
            enclog = analyze_enclog(log_path)
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
