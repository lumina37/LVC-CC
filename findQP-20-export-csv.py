import argparse
import csv
import json
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, gen_infomap

# Config from CMD
parser = argparse.ArgumentParser(description="Export proc metrics to csv")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))


# Export
summary_dir = config.dir.output / "summary"
src_dir = summary_dir / "tasks"
dst_dir = summary_dir / "csv"
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


with (dst_dir / "proc.csv").open("w", encoding="utf-8", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    headers = [
        "Sequence",
        "QP",
        "Bitrate",
        "LLPSNR-Y",
        "LLPSNR-U",
        "LLPSNR-V",
        "MVPSNR-Y",
        "MVPSNR-U",
        "MVPSNR-V",
    ]
    csv_writer.writerow(headers)

    for seq_name in config.seqs:
        tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

        anchorQPs = config.anchorQP.get(seq_name, None)
        if not anchorQPs:
            continue

        extendQP = config.proc.get("extendQP", 0)
        crop_size = config.proc["crop_size"][seq_name]
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)
        for qp in range(anchorQPs[0] - extendQP, anchorQPs[-1] + 1):
            tcodec = CodecTask(qp=qp).follow(tpreproc)
            tpostproc = PostprocTask().follow(tcodec)
            tconvert = Convert40Task(views=config.views).follow(tpostproc)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                csv_writer.writerow(["Not Found"] + [0] * (len(headers) - 1))

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            csv_writer.writerow(
                [
                    seq_name,
                    qp,
                    metrics["bitrate"],
                    metrics["llpsnr_y"],
                    metrics["llpsnr_u"],
                    metrics["llpsnr_v"],
                    metrics["mvpsnr_y"],
                    metrics["mvpsnr_u"],
                    metrics["mvpsnr_v"],
                ]
            )


with (dst_dir / "anchor.csv").open("w", encoding="utf-8", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    headers = [
        "Sequence",
        "QP",
        "Bitrate",
        "LLPSNR-Y",
        "LLPSNR-U",
        "LLPSNR-V",
        "MVPSNR-Y",
        "MVPSNR-U",
        "MVPSNR-V",
    ]
    csv_writer.writerow(headers)

    for seq_name in config.seqs:
        tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

        anchorQPs = config.anchorQP.get(seq_name, None)
        if not anchorQPs:
            continue

        for qp in anchorQPs:
            tcodec = CodecTask(qp=qp).follow(tcopy)
            tconvert = Convert40Task(views=config.views).follow(tcodec)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                csv_writer.writerow(["Not Found"] + [0] * (len(headers) - 1))

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            csv_writer.writerow(
                [
                    seq_name,
                    qp,
                    metrics["bitrate"],
                    metrics["llpsnr_y"],
                    metrics["llpsnr_u"],
                    metrics["llpsnr_v"],
                    metrics["mvpsnr_y"],
                    metrics["mvpsnr_u"],
                    metrics["mvpsnr_v"],
                ]
            )
