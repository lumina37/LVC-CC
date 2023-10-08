import dataclasses
import json
import re
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root

log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['common']['compute']


@dataclasses.dataclass
class PSNR:
    y: float = 0.0
    u: float = 0.0
    v: float = 0.0

    def __iadd__(self, rhs: "PSNR") -> "PSNR":
        self.y += rhs.y
        self.u += rhs.u
        self.v += rhs.v
        return self

    def __itruediv__(self, d: float) -> "PSNR":
        self.y /= d
        self.u /= d
        self.v /= d
        return self


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


def compute_yuv(lhs: Path, rhs: Path, width: int, height: int) -> PSNR:
    lhs_size = lhs.stat().st_size
    rhs_size = rhs.stat().st_size
    assert lhs_size == rhs_size

    ysize = width * height
    uvsize = int(ysize / 4)
    frames = rootcfg['frames']

    psnr = PSNR()

    with lhs.open('rb', buffering=ysize) as lhs_file, rhs.open('rb', buffering=ysize) as rhs_file:
        for _ in range(frames):
            lhs_buff = lhs_file.read(ysize)
            rhs_buff = rhs_file.read(ysize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr.y += compite_psnr_f64array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr.u += compite_psnr_f64array(lhs_arr, rhs_arr)

            lhs_buff = lhs_file.read(uvsize)
            rhs_buff = rhs_file.read(uvsize)
            lhs_arr = np.frombuffer(lhs_buff, np.uint8).astype(np.float64) / 255.0
            rhs_arr = np.frombuffer(rhs_buff, np.uint8).astype(np.float64) / 255.0
            psnr.v += compite_psnr_f64array(lhs_arr, rhs_arr)

    psnr /= frames

    return psnr


src_dirs = path_from_root(rootcfg, rootcfg['common']['compose']['dst'])


dst_dir = path_from_root(rootcfg, cfg['dst'])
mkdir(dst_dir)

main_dic = {}

for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name
    width, height = get_wh(seq_name)
    seq_dic: dict = main_dic.setdefault(seq_name, {})

    for tp in ['pre', 'wopre']:
        tp_dic: dict = seq_dic.setdefault(tp, {})

        for qp_dir in (src_dir / tp).iterdir():
            if not qp_dir.is_dir():
                continue

            qp = get_QP(qp_dir.name)
            log.debug(f"processing {tp} seq: {seq_name}. QP={qp}")
            QPs: list = tp_dic.setdefault('QP', [])
            QPs.append(qp)

            codec_dir = path_from_root(rootcfg, rootcfg[tp]['codec']['dst'])
            codec_log_p = (codec_dir / seq_name / qp_dir.name).with_suffix('.log')
            bitrate = get_bitrate(codec_log_p)
            bitrates: list = tp_dic.setdefault('bitrate', [])
            bitrates.append(bitrate)

            psnr = PSNR()
            count = 0
            for pre_p in qp_dir.glob('*.yuv'):
                psnr += compute_yuv(src_dir / 'base' / pre_p.name, pre_p, width, height)
                count += 1

            psnr /= count

            ypsnrs: list = tp_dic.setdefault('Y-PSNR', [])
            ypsnrs.append(psnr.y)
            upsnrs: list = tp_dic.setdefault('U-PSNR', [])
            upsnrs.append(psnr.u)
            vpsnrs: list = tp_dic.setdefault('V-PSNR', [])
            vpsnrs.append(psnr.v)

with (dst_dir / 'psnr.json').open('w') as f:
    json.dump(main_dic, f, indent=2)
