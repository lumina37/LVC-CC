import argparse
import json
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, gen_infomap

parser = argparse.ArgumentParser(description="Export RD-curve")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base",
    "-b",
    type=str,
    default="base.toml",
    help="base config, recommend to store some immutable directory settings",
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

summary_dir = config.dir.output / "summary"
src_dir = summary_dir / "tasks"
dst_dir = summary_dir / "figure"
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    tpreproc = PreprocTask().follow(tcopy)

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

    offsetQP = config.proc.get("offsetQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)

        proc_bitrates = []
        proc_psnrs = []
        for anchorQP in config.anchorQP.get(seq_name, []):
            qp = anchorQP + offsetQP
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

        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = tpreproc.tag
        ax.set_title(title)

        ax.plot(anchor_bitrates, anchor_psnrs, label="anchor")
        ax.plot(proc_bitrates, proc_psnrs, label="proc")
        ax.legend()

        fig.savefig((dst_dir / tpreproc.tag).with_suffix(".png"))
        fig.savefig((dst_dir / tpreproc.tag).with_suffix(".svg"))
