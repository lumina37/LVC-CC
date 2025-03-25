import argparse
import json
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, gen_infomap

# Config from CMD
parser = argparse.ArgumentParser(description="Export RD-curve")

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
dst_dir = summary_dir / "figure"
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    tpreproc = PreprocTask().follow(tcopy)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax: Axes = ax
    ax.set_xlabel("Total bitrate (Kbps)")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title(seq_name)

    anchor_bitrates = []
    anchor_psnrs = []
    anchorQPs = config.anchorQP.get(seq_name, [])
    for qp in anchorQPs:
        tcodec = CodecTask(qp=qp).follow(tcopy)
        tconvert = Convert40Task(views=config.views).follow(tcodec)

        json_path = src_dir / tcodec.tag / "psnr.json"
        if not json_path.exists():
            continue

        with json_path.open(encoding="utf-8") as f:
            metrics: dict = json.load(f)

        anchor_bitrates.append(metrics["bitrate"])
        anchor_psnrs.append(metrics["mvpsnr_y"])

    ax.plot(anchor_bitrates, anchor_psnrs, label="anchor", color="blue")
    for i in range(len(anchor_bitrates)):
        ax.annotate(
            str(anchorQPs[i]),
            xy=(anchor_bitrates[i], anchor_psnrs[i]),
            xytext=(-5, 0),
            textcoords="offset points",
            color="blue",
        )

    # With Pre/Postprocess
    proc_bitrates = []
    proc_psnrs = []
    procQPs = config.proc["QP"].get(seq_name, [])
    for qp in procQPs:
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

    ax.plot(proc_bitrates, proc_psnrs, label="proc", color="orange")
    for i in range(len(proc_bitrates)):
        ax.annotate(
            str(procQPs[i]),
            xy=(proc_bitrates[i], proc_psnrs[i]),
            xytext=(-5, 0),
            textcoords="offset points",
            color="orange",
        )

    ax.legend()

    fig.savefig((dst_dir / seq_name).with_suffix(".png"))
