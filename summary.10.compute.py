import dataclasses
import json
import re
from pathlib import Path
from typing import Tuple

import cv2 as cv
import numpy as np

from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')


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
    render_dir = get_root() / "playground/base/render" / seq_name
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
    frames = rootcfg['common']['frames']

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


src_root = get_root() / "playground/summary/compose"
dst_dir = get_root() / "playground/summary/compute"
mkdir(dst_dir)

main_dic = {}

for pre_type in ['wMCA', 'woMCA']:
    for vtm_type in rootcfg['common']['vtm_types']:
        vtm_type: str = vtm_type

        for seq_name in rootcfg['common']['seqs']:
            seq_name: str = seq_name

            src_dir = src_root / seq_name / pre_type / vtm_type
            width, height = get_wh(seq_name)
            seq_dic: dict = main_dic.setdefault(seq_name, {})

            pre_type_dic: dict = seq_dic.setdefault(pre_type, {})
            vtm_dic: dict = pre_type_dic.setdefault(vtm_type, {})

            for qp in rootcfg['qp'][pre_type][seq_name]:
                log.debug(f"pre_type={pre_type}, vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}")

                qp_str = f"QP#{qp}"
                qp_dir = src_dir / qp_str

                QPs: list = vtm_dic.setdefault('QP', [])
                QPs.append(qp)

                codec_dir = get_root() / "playground" / pre_type / "codec" / vtm_type
                codec_log_p = (codec_dir / seq_name / qp_str).with_suffix('.log')
                bitrate = get_bitrate(codec_log_p)
                bitrates: list = vtm_dic.setdefault('bitrate', [])
                bitrates.append(bitrate)

                psnr = PSNR()
                count = 0
                for pre_p in qp_dir.glob('*.yuv'):
                    psnr += compute_yuv(src_root / seq_name / 'base' / pre_p.name, pre_p, width, height)
                    count += 1
                psnr /= count

                ypsnrs: list = vtm_dic.setdefault('Y-PSNR', [])
                ypsnrs.append(psnr.y)
                upsnrs: list = vtm_dic.setdefault('U-PSNR', [])
                upsnrs.append(psnr.u)
                vpsnrs: list = vtm_dic.setdefault('V-PSNR', [])
                vpsnrs.append(psnr.v)


with (dst_dir / 'psnr.json').open('w') as f:
    json.dump(main_dic, f, indent=2)
