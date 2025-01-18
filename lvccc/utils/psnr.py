from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import yuvio

from ..helper import get_any_file, size_from_filename
from ..task import CodecTask, ConvertTask, PostprocTask
from ..task.infomap import query
from .backtrack import get_ancestor, is_anchor

if TYPE_CHECKING:
    from pathlib import Path


def calc_array_mse(lhs: np.ndarray, rhs: np.ndarray) -> float:
    diff = lhs.astype(np.int16) - rhs.astype(np.int16)
    sqrdiff = np.square(diff)
    mse = np.mean(sqrdiff)
    return mse


def calc_yuv_psnr(lhs: Path, rhs: Path, width: int, height: int) -> np.ndarray:
    lhs_reader = yuvio.get_reader(lhs, width, height, "yuv420p")
    rhs_reader = yuvio.get_reader(rhs, width, height, "yuv420p")
    if len(lhs_reader) != len(rhs_reader):
        raise RuntimeError(f"Frame count not equal! lhs={lhs} rhs={rhs}")

    mse_acc = np.zeros(3)
    count = 0

    for lhs_frame, rhs_frame in zip(lhs_reader, rhs_reader, strict=True):
        mse_acc[0] += calc_array_mse(lhs_frame.y, rhs_frame.y)
        mse_acc[1] += calc_array_mse(lhs_frame.u, rhs_frame.u)
        mse_acc[2] += calc_array_mse(lhs_frame.v, rhs_frame.v)
        count += 1

    psnr = 20.0 * np.log10(255.0 / np.sqrt(mse_acc / count))

    return psnr


def calc_mv_psnr(task: ConvertTask) -> np.ndarray:
    copy_task = task.chain[0]
    base_task = task.__class__(views=task.views).with_parent(copy_task)

    base_dir = query(base_task) / "yuv"
    self_dir = query(task) / "yuv"

    width, height = size_from_filename(get_any_file(base_dir, "*.yuv").name)

    channels = 3
    accpsnr = np.zeros(channels)

    lhss = sorted(base_dir.iterdir())
    rhss = sorted(self_dir.iterdir())
    count = len(lhss)

    for lhs, rhs in zip(lhss, rhss, strict=True):
        accpsnr += calc_yuv_psnr(lhs, rhs, width, height)
    accpsnr /= count

    return accpsnr


def calc_lenslet_psnr(task: ConvertTask) -> np.ndarray:
    copy_task = task.chain[0]
    if is_anchor(task):
        cmp_task = get_ancestor(task, CodecTask)
    else:
        cmp_task = get_ancestor(task, PostprocTask)

    lhs = get_any_file(query(copy_task), "*.yuv")
    rhs = get_any_file(query(cmp_task), "*.yuv")

    width, height = size_from_filename(lhs.name)

    psnr = calc_yuv_psnr(lhs, rhs, width, height)
    return psnr
