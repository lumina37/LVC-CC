import argparse
import csv
import json
from pathlib import Path

import numpy as np
import scipy.interpolate

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask


def BD_PSNR(R1, PSNR1, R2, PSNR2, piecewise=0):
    lR1 = np.log(R1)
    lR2 = np.log(R2)

    PSNR1 = np.array(PSNR1)
    PSNR2 = np.array(PSNR2)

    p1 = np.polyfit(lR1, PSNR1, 3)
    p2 = np.polyfit(lR2, PSNR2, 3)

    # integration interval
    min_int = max(min(lR1), min(lR2))
    max_int = min(max(lR1), max(lR2))

    # find integral
    if piecewise == 0:
        p_int1 = np.polyint(p1)
        p_int2 = np.polyint(p2)

        int1 = np.polyval(p_int1, max_int) - np.polyval(p_int1, min_int)
        int2 = np.polyval(p_int2, max_int) - np.polyval(p_int2, min_int)
    else:
        # See https://chromium.googlesource.com/webm/contributor-guide/+/master/scripts/visual_metrics.py
        lin = np.linspace(min_int, max_int, num=100, retstep=True)
        interval = lin[1]
        samples = lin[0]
        v1 = scipy.interpolate.pchip_interpolate(np.sort(lR1), PSNR1[np.argsort(lR1)], samples)
        v2 = scipy.interpolate.pchip_interpolate(np.sort(lR2), PSNR2[np.argsort(lR2)], samples)
        # Calculate the integral using the trapezoid method on the samples.
        int1 = np.trapezoid(v1, dx=interval)
        int2 = np.trapezoid(v2, dx=interval)

    # find avg diff
    avg_diff = (int2 - int1) / (max_int - min_int)

    return avg_diff


def BD_RATE(R1, PSNR1, R2, PSNR2, piecewise=0):
    lR1 = np.log(R1)
    lR2 = np.log(R2)

    # rate method
    p1 = np.polyfit(PSNR1, lR1, 3)
    p2 = np.polyfit(PSNR2, lR2, 3)

    # integration interval
    min_int = max(min(PSNR1), min(PSNR2))
    max_int = min(max(PSNR1), max(PSNR2))

    # find integral
    if piecewise == 0:
        p_int1 = np.polyint(p1)
        p_int2 = np.polyint(p2)

        int1 = np.polyval(p_int1, max_int) - np.polyval(p_int1, min_int)
        int2 = np.polyval(p_int2, max_int) - np.polyval(p_int2, min_int)
    else:
        lin = np.linspace(min_int, max_int, num=100, retstep=True)
        interval = lin[1]
        samples = lin[0]
        v1 = scipy.interpolate.pchip_interpolate(np.sort(PSNR1), lR1[np.argsort(PSNR1)], samples)
        v2 = scipy.interpolate.pchip_interpolate(np.sort(PSNR2), lR2[np.argsort(PSNR2)], samples)
        # Calculate the integral using the trapezoid method on the samples.
        int1 = np.trapezoid(v1, dx=interval)
        int2 = np.trapezoid(v2, dx=interval)

    # find avg diff
    avg_exp_diff = (int2 - int1) / (max_int - min_int)
    avg_diff = (np.exp(avg_exp_diff) - 1) * 100
    return avg_diff


# Config from CMD
parser = argparse.ArgumentParser(description="Export BD-rate")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()


# Export
config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

summary_dir = config.dir.output / "summary"
src_dir = summary_dir / "tasks"
dst_dir = summary_dir / "csv"
mkdir(dst_dir)
csv_path = dst_dir / "bdrate.csv"

with csv_path.open("w", encoding="utf-8", newline="") as csv_f:
    csv_writer = csv.writer(csv_f)
    headers = ["Sequence", "CropSize", "BD-rate"]
    csv_writer.writerow(headers)

    for seq_name in config.seqs:
        tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

        anchorQPs = config.anchorQP.get(seq_name, None)
        if not anchorQPs:
            continue

        anchor_bitrates = []
        anchor_psnrs = []
        for qp in config.anchorQP.get(seq_name, []):
            tcodec = CodecTask(qp=qp).follow(tcopy)
            tconvert = Convert40Task(views=config.views).follow(tcodec)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                continue

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            anchor_bitrates.append(metrics["bitrate"])
            anchor_psnrs.append(metrics["mvpsnr_y"])

        extendQP = config.proc.get("extendQP", 0)
        for crop_size in config.proc["crop_size"].get(seq_name, []):
            row = [seq_name, str(crop_size)]
            tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)

            proc_bitrates = []
            proc_psnrs = []
            for qp in range(anchorQPs[0] - extendQP, anchorQPs[-1]):
                tcodec = CodecTask(qp=qp).follow(tpreproc)
                tpostproc = PostprocTask().follow(tcodec)
                tconvert = Convert40Task(views=config.views).follow(tpostproc)

                json_path = src_dir / tcodec.tag / "psnr.json"
                if not json_path.exists():
                    continue

                with json_path.open(encoding="utf-8") as f:
                    metrics: dict = json.load(f)

                proc_bitrates.append(metrics["bitrate"])
                proc_psnrs.append(metrics["mvpsnr_y"])

            bdrate = BD_RATE(
                anchor_bitrates,
                anchor_psnrs,
                proc_bitrates,
                proc_psnrs,
                piecewise=1,
            )
            row.append(f"{bdrate}%")

            csv_writer.writerow(row)
