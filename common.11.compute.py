import dataclasses
import re
from pathlib import Path

import cv2 as cv

from vvchelper.command import render
from vvchelper.config.raytrix import RaytrixCfg
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root


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


all_cfg = from_file('pipeline.toml')


@dataclasses.dataclass
class PSNR:
    y: float = 0.0
    u: float = 0.0
    v: float = 0.0


@dataclasses.dataclass
class Metric:
    psnr: PSNR = dataclasses.field(default_factory=PSNR)
    bitrate: float = dataclasses.field(default_factory=dict)


metrics_pre: dict[str, Metric] = {}
metrics_wopre: dict[str, Metric] = {}


class ImgBase:
    def __init__(self, img) -> None:
        yuv = cv.cvtColor(img, cv.COLOR_BGR2YUV)
        self.y, self.u, self.v = cv.split(yuv)


base_dirs = path_from_root(all_cfg, all_cfg['base']['render']['dst'])
for base_dir in base_dirs.iterdir():
    if not base_dir.is_dir():
        continue

    seq_name = base_dir.name

    frame_count = len(list(base_dir.glob('frame#*')))

    for frame_dir in base_dir.glob('frame#*'):
        if not frame_dir.is_dir():
            continue

        bases = [ImgBase(cv.imread(str(p))) for p in frame_dir.glob("image*")]
        count = frame_count * len(bases)

        wopre_dir = path_from_root(all_cfg, all_cfg['pre']['render']['dst'])
        for qp_dir in (wopre_dir / seq_name).glob('QP#*'):
            if not qp_dir.is_dir():
                continue

            qp = get_QP(qp_dir.name)
            task_name = f"{seq_name}_{qp}"
            metrics_pre.setdefault(task_name, Metric())

            codec_dir = path_from_root(all_cfg, all_cfg['pre']['codec']['dst']) / seq_name
            log_path = codec_dir / f'{qp_dir.name}.log'
            metrics_pre[task_name].bitrate = get_bitrate(log_path)

            for idx, img_path in enumerate((qp_dir / frame_dir.name).glob("image*")):
                cmp = ImgBase(cv.imread(str(img_path)))
                metrics_pre[task_name].psnr.y += cv.quality.QualityPSNR_compute(bases[idx].y, cmp.y)[0][0] / count
                metrics_pre[task_name].psnr.u += cv.quality.QualityPSNR_compute(bases[idx].u, cmp.u)[0][0] / count
                metrics_pre[task_name].psnr.v += cv.quality.QualityPSNR_compute(bases[idx].v, cmp.v)[0][0] / count

        wopre_dir = path_from_root(all_cfg, all_cfg['wopre']['render']['dst'])
        for qp_dir in (wopre_dir / seq_name).glob('QP#*'):
            if not qp_dir.is_dir():
                continue

            qp = get_QP(qp_dir.name)
            task_name = f"{seq_name}_{qp}"
            metrics_wopre.setdefault(task_name, Metric())

            codec_dir = path_from_root(all_cfg, all_cfg['wopre']['codec']['dst']) / seq_name
            log_path = codec_dir / f'{qp_dir.name}.log'
            metrics_wopre[task_name].bitrate = get_bitrate(log_path)

            for idx, img_path in enumerate((qp_dir / frame_dir.name).glob("image*")):
                cmp = ImgBase(cv.imread(str(img_path)))
                metrics_wopre[task_name].psnr.y += cv.quality.QualityPSNR_compute(bases[idx].y, cmp.y)[0][0] / count
                metrics_wopre[task_name].psnr.u += cv.quality.QualityPSNR_compute(bases[idx].u, cmp.u)[0][0] / count
                metrics_wopre[task_name].psnr.v += cv.quality.QualityPSNR_compute(bases[idx].v, cmp.v)[0][0] / count

with open("metrics_pre.txt", 'w') as f:
    for name, metric in metrics_pre.items():
        f.write(f"{name}\t{metric.bitrate}\t{metric.psnr.y}\t{metric.psnr.u}\t{metric.psnr.v}\t{999.9}\t{99.9}\n")
with open("metrics_wopre.txt", 'w') as f:
    for name, metric in metrics_wopre.items():
        f.write(f"{name}\t{metric.bitrate}\t{metric.psnr.y}\t{metric.psnr.u}\t{metric.psnr.v}\t{999.9}\t{99.9}\n")
