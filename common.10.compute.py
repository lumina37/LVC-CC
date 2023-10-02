import csv
import dataclasses
import re
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root


@dataclasses.dataclass
class PSNR:
    y: float = 0.0
    u: float = 0.0
    v: float = 0.0
    avg: float = 0.0


log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['common']['compute']

src_dirs = path_from_root(rootcfg, rootcfg['common']['compose']['dst'])


def get_bitrate(fp: Path) -> float:
    with fp.open('r') as f:
        layerid_row_idx = -128
        for i, row in enumerate(f.readlines()):
            if row.startswith('LayerId'):
                layerid_row_idx = i
            if i == layerid_row_idx + 2:
                num_strs = re.findall(r"\d+\.?\d*", row)
                bitrate_str = num_strs[1]
                return float(bitrate_str)


def get_wh(seq_name: str) -> Tuple[int, int]:
    render_dir = path_from_root(rootcfg, rootcfg['base']['render']['dst']) / seq_name
    frame_dir = next(render_dir.glob('frame#*'))
    img_ref_p = next(frame_dir.glob('*.png'))
    img_ref = cv.imread(str(img_ref_p))
    height, width = img_ref.shape[:2]
    return (height, width)


def compite_psnr_f64array(lhs: np.ndarray, rhs: np.ndarray) -> float:
    mse = np.mean((lhs - rhs) ** 2)
    psnr = np.log10(1.0 / mse) * 10.0
    return psnr


def compute_yuv(lhs: Path, rhs: Path, width: int, height: int):
    lhs_size = lhs.stat().st_size
    rhs_size = rhs.stat().st_size
    assert lhs_size == rhs_size

    ysize = width * height
    uvsize = int(ysize / 4)
    frames = int(lhs_size / (ysize + uvsize * 2))
    assert frames == 30

    ypsnr = 0.0
    upsnr = 0.0
    vpsnr = 0.0

    with lhs.open('rb', buffering=ysize) as lhs_file, rhs.open('rb', buffering=ysize) as rhs_file:
        for _ in range(frames):
            lhs_buff = lhs_file.read(ysize)
            rhs_buff = rhs_file.read(ysize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            ypsnr += compite_psnr_f64array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            upsnr += compite_psnr_f64array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            vpsnr += compite_psnr_f64array(lhs_arr, rhs_arr)

    ypsnr /= frames
    upsnr /= frames
    vpsnr /= frames

    return (ypsnr, upsnr, vpsnr)


dst_dir = path_from_root(rootcfg, cfg['dst'])
mkdir(dst_dir)

for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name
    width, height = get_wh(seq_name)

    def compute_type(tp: str):
        with (dst_dir / f'metrics_{tp}.csv').open('w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            header = ["name", "QP", "bitrate", "yPSNR", "uPSNR", "vPSNR"]
            csv_writer.writerow(header)

            for qp_dir in (src_dir / tp).iterdir():
                if not qp_dir.is_dir():
                    continue

                qp = get_QP(qp_dir.name)
                codec_dir = path_from_root(rootcfg, rootcfg[tp]['codec']['dst'])
                codec_log_p = (codec_dir / seq_name / qp_dir.name).with_suffix('.log')
                bitrate = get_bitrate(codec_log_p)

                ypsnr = 0.0
                upsnr = 0.0
                vpsnr = 0.0
                count = 0
                for pre_p in qp_dir.glob('*.yuv'):
                    _ypsnr, _upsnr, _vpsnr = compute_yuv(src_dir / 'base' / pre_p.name, pre_p, width, height)
                    ypsnr += _ypsnr
                    upsnr += _upsnr
                    vpsnr += _vpsnr
                    count += 1

                assert count == 25  # Remove this as you like
                ypsnr /= count
                upsnr /= count
                vpsnr /= count

                csv_writer.writerow([seq_name, qp, bitrate, ypsnr, upsnr, vpsnr])

    compute_type('pre')
    compute_type('wopre')
