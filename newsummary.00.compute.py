import json
import re
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from mcahelper.cfg import node
from mcahelper.logging import get_logger
from mcahelper.task import CodecTask, PreprocTask, RenderTask, iterator
from mcahelper.task.infomap import query
from mcahelper.utils import get_first_file, mkdir, run_cmds

node_cfg = node.set_node_cfg('node-cfg.toml')

log = get_logger()


BASES: dict[str, Path] = {}
FRAMES = 1


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
                "-vframes",
                task.frames,
                dstdir / f"{row_idx}-{col_idx}.yuv",
                "-v",
                "warning",
                "-y",
            ]
            run_cmds(cmds)

            view_idx += 1


def get_codec_task(rtask: RenderTask) -> CodecTask:
    for i, task_dic in enumerate(rtask.chains):
        if task_dic['task'] == CodecTask.task:
            ctask = CodecTask(**task_dic, chains=rtask.chains[:i])
            return ctask


def get_bitrate_from_fp(fp: Path) -> float:
    with fp.open('r') as f:
        layerid_row_idx = -128
        for i, row in enumerate(f.readlines()):
            if row.startswith('LayerId'):
                layerid_row_idx = i
            if i == layerid_row_idx + 2:
                num_strs = re.findall(r"\d+\.?\d*", row)
                bitrate_str = num_strs[1]
                return float(bitrate_str)


def get_wh(task: RenderTask) -> Tuple[int, int]:
    render_dir = query(task) / 'img'
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
    uvsize = int(ysize / 4)

    psnr = np.zeros(3)

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


def compute_psnr_task(task: RenderTask) -> np.ndarray:
    basedir = BASES[task.seq_name]
    yuvdir = query(task) / "yuv"

    width, height = get_wh(task)

    psnr = np.zeros(3)
    count = 0
    for lhs, rhs in zip(basedir.iterdir(), yuvdir.iterdir(), strict=True):
        psnr += compute_psnr_yuv(lhs, rhs, task.frames, width, height)
        count += 1
    psnr /= count

    return psnr


for task in iterator.tasks(RenderTask, lambda t: not t.chains):
    if task.frames != FRAMES:
        continue
    if task.seq_name not in node_cfg.cases.seqs:
        continue

    log.info(f"Handling {task}")
    compose(task)
    dstdir = query(task) / "yuv"
    BASES[task.seq_name] = dstdir

main_dic = {}

for task in iterator.tasks(RenderTask, lambda t: t.chains):
    if task.frames != FRAMES:
        continue
    if task.seq_name not in node_cfg.cases.seqs:
        continue

    log.info(f"Handling {task}")
    compose(task)

    seq_dic: dict = main_dic.setdefault(task.seq_name, {})

    ctask = get_codec_task(task)

    pre_type = 'wMCA' if ctask.chains[0]['task'] == PreprocTask.task else 'woMCA'
    pre_type_dic: dict = seq_dic.setdefault(pre_type, {})

    vtm_dic: dict = pre_type_dic.setdefault(ctask.vtm_type, {})

    log_path = query(ctask) / "out.log"
    bitrate = get_bitrate_from_fp(log_path)
    bitrates: list = vtm_dic.setdefault('bitrate', [])
    bitrates.append(bitrate)

    psnr = compute_psnr_task(task)

    QPs: list = vtm_dic.setdefault('QP', [])
    QPs.append(ctask.QP)

    ypsnrs: list = vtm_dic.setdefault('Y-PSNR', [])
    ypsnrs.append(psnr[0])
    upsnrs: list = vtm_dic.setdefault('U-PSNR', [])
    upsnrs.append(psnr[1])
    vpsnrs: list = vtm_dic.setdefault('V-PSNR', [])
    vpsnrs.append(psnr[2])

summary_dir = node_cfg.path.dataset / 'summary'
mkdir(summary_dir)
with (summary_dir / 'psnr.json').open('w') as f:
    json.dump(main_dic, f, indent=2)
