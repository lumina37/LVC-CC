import dataclasses
import re
from pathlib import Path

import cv2 as cv

from vvchelper.config.self import Cfg


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


cfg = Cfg.from_file(Path('pipeline.toml'))
compute_cfg = cfg.computation


@dataclasses.dataclass
class PSNR:
    y: float = 0.0
    u: float = 0.0
    v: float = 0.0


@dataclasses.dataclass
class Metric:
    psnr: PSNR = dataclasses.field(default_factory=PSNR)
    bitrate: float = dataclasses.field(default_factory=dict)


metrics: dict[str, Metric] = {}
metrics_ref: dict[str, Metric] = {}


class ImgBase:
    def __init__(self, img) -> None:
        yuv = cv.cvtColor(img, cv.COLOR_BGR2YUV)
        self.y, self.u, self.v = cv.split(yuv)



for dataset_dir in cfg.dataset_root.iterdir():
    base_dir = dataset_dir / compute_cfg.base_dir
    print(f"Handling: {dataset_dir.name}")

    frame_count = len(list(base_dir.iterdir()))
    real_count = 0

    for frame_dir in base_dir.iterdir():
        bases = [ImgBase(cv.imread(str(imgp))) for imgp in frame_dir.glob("image*")]
        count = frame_count * len(bases)

        for render_dir in (dataset_dir / compute_cfg.render_dirs).iterdir():
            qp = int(render_dir.name)
            task_name = f"{dataset_dir.name}_{qp}"
            metrics.setdefault(task_name, Metric())

            log_file_str = compute_cfg.log_file_fstr.format(qp=qp)
            metrics[task_name].bitrate = get_bitrate(dataset_dir / log_file_str)

            for idx, img_path in enumerate((render_dir / frame_dir.name).glob("image*")):
                cmp = ImgBase(cv.imread(str(img_path)))
                metrics[task_name].psnr.y += cv.quality.QualityPSNR_compute(bases[idx].y, cmp.y)[0][0] / count
                metrics[task_name].psnr.u += cv.quality.QualityPSNR_compute(bases[idx].u, cmp.u)[0][0] / count
                metrics[task_name].psnr.v += cv.quality.QualityPSNR_compute(bases[idx].v, cmp.v)[0][0] / count
                real_count += 1

        for render_ref_dir in (dataset_dir / compute_cfg.render_ref_dirs).iterdir():
            qp = int(render_ref_dir.name)
            task_name = f"{dataset_dir.name}_{qp}"
            metrics_ref.setdefault(task_name, Metric())

            ref_log_file_str = compute_cfg.ref_log_file_fstr.format(qp=qp)
            metrics_ref[task_name].bitrate = get_bitrate(dataset_dir / ref_log_file_str)

            for idx, img_path in enumerate((render_ref_dir / frame_dir.name).glob("image*")):
                cmp = ImgBase(cv.imread(str(img_path)))
                metrics_ref[task_name].psnr.y += cv.quality.QualityPSNR_compute(bases[idx].y, cmp.y)[0][0] / count
                metrics_ref[task_name].psnr.u += cv.quality.QualityPSNR_compute(bases[idx].u, cmp.u)[0][0] / count
                metrics_ref[task_name].psnr.v += cv.quality.QualityPSNR_compute(bases[idx].v, cmp.v)[0][0] / count

with open("metrics.txt", 'w') as f:
    for name, metric in metrics.items():
        f.write(f"{name}\t{metric.bitrate}\t{metric.psnr.y}\t{metric.psnr.u}\t{metric.psnr.v}\t{999.9}\t{99.9}\n")
with open("metrics_ref.txt", 'w') as f:
    for name, metric in metrics_ref.items():
        f.write(f"{name}\t{metric.bitrate}\t{metric.psnr.y}\t{metric.psnr.u}\t{metric.psnr.v}\t{999.9}\t{99.9}\n")
