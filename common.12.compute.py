import dataclasses
import re
from pathlib import Path

import cv2 as cv

from vvchelper.command import render
from vvchelper.config.raytrix import RaytrixCfg
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

all_cfg = from_file('pipeline.toml')
cfg = all_cfg['common']['compute']

src_dirs = path_from_root(all_cfg, all_cfg['common']['compose']['dst'])


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


def compute_yuv(lhs: Path, rhs: Path, width: int, height: int):
    lhs_file = lhs.open('rb', buffering=4096)
    rhs_file = rhs.open('rb', buffering=4096)
