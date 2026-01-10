import argparse
import csv
import json
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import Convert45Task, CopyTask, DecodeTask, EncodeTask, gen_infomap

# Config from CMD
parser = argparse.ArgumentParser(description="Export anchor metrics to csv")

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


with (dst_dir / "anchor.csv").open("w", encoding="utf-8", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    headers = [
        "Sequence",
        "QP",
        "Bitrate (kb/s)",
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

        for qp in config.anchorQP.get(seq_name, []):
            tenc = EncodeTask(qp=qp).follow(tcopy)
            tdec = DecodeTask().follow(tenc)
            tconvert = Convert45Task(views=config.views).follow(tdec)

            json_path = src_dir / tenc.tag / "psnr.json"
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
