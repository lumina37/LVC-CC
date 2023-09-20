import math
import re
from pathlib import Path

import cv2 as cv

from helper.configs.self import Cfg


def bgr2y(img):
    return cv.cvtColor(img, cv.COLOR_BGR2YUV)[:, :, 0]


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

mses = {}
mses_ref = {}
bitrates = {}
bitrates_ref = {}

for dataset_dir in cfg.dataset_root.iterdir():
    baseline_dir = dataset_dir / compute_cfg.baseline_dir

    frame_count = len(list(baseline_dir.iterdir()))

    for frame_id in range(1, frame_count + 1):
        frame_id_str = f"{frame_id:0>3}"
        baselines = [bgr2y(cv.imread(str(p))) for p in (baseline_dir / frame_id_str).glob("image*")]
        count = frame_count * len(baselines)

        for render_dir in (dataset_dir / compute_cfg.render_dirs).iterdir():
            qp = int(render_dir.name)
            task_name = f"{dataset_dir.name}_{qp}"

            log_file_str = compute_cfg.log_file_fstr.format(qp=qp)
            bitrates[task_name] = get_bitrate(dataset_dir / log_file_str)

            mse_frame_acc = 0.0
            for base, img_path in zip(baselines, (render_dir / frame_id_str).glob("image*")):
                cmp = bgr2y(cv.imread(str(img_path)))
                mse = cv.quality.QualityMSE_compute(base, cmp)[0][0]
                mse_frame_acc += mse

            mses[task_name] = mses.get(task_name, 0.0) + mse_frame_acc / count

        for render_ref_dir in (dataset_dir / compute_cfg.render_ref_dirs).iterdir():
            qp = int(render_ref_dir.name)
            task_name = f"{dataset_dir.name}_{qp}"

            ref_log_file_str = compute_cfg.ref_log_file_fstr.format(qp=qp)
            bitrates_ref[task_name] = get_bitrate(dataset_dir / ref_log_file_str)

            mse_frame_acc = 0.0
            for base, img_path in zip(baselines, (render_ref_dir / frame_id_str).glob("image*")):
                cmp = bgr2y(cv.imread(str(img_path)))
                mse = cv.quality.QualityMSE_compute(base, cmp)[0][0]
                mse_frame_acc += mse

            mses_ref[task_name] = mses_ref.get(task_name, 0.0) + mse_frame_acc / count

with open("metrics_ref.txt", 'w') as f:
    for (k, mse), bitrate in zip(mses_ref.items(), bitrates_ref.values()):
        psnr = 10 * math.log10(255**2 / mse) if mse else 0.0
        f.write(f"{k}\t{bitrate}\t{psnr}\t{1.0}\t{1.0}\t{999.9}\t{99.9}\n")
with open("metrics.txt", 'w') as f:
    for (k, mse), bitrate in zip(mses.items(), bitrates.values()):
        psnr = 10 * math.log10(255**2 / mse) if mse else 0.0
        f.write(f"{k}\t{bitrate}\t{psnr}\t{1.0}\t{1.0}\t{999.9}\t{99.9}\n")
