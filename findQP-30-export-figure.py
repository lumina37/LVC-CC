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


# Export
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

    startQP = config.proc.get("startQP", 0)
    endQP = config.proc.get("endQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = tpreproc.tag
        ax.set_title(title)

        proc_bitrates = []
        proc_psnrs = []
        procQPs = []
        for anchorQP in anchorQPs:
            for offsetQP in range(startQP, endQP):
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
                procQPs.append(qp)

        ax.plot(anchor_bitrates, anchor_psnrs, label="anchor", color="blue")
        for i in range(len(anchor_bitrates)):
            ax.annotate(
                str(anchorQPs[i]),
                xy=(anchor_bitrates[i], anchor_psnrs[i]),
                xytext=(-5, 0),
                textcoords="offset points",
                color="blue",
            )

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

        fig.savefig((dst_dir / tpreproc.tag).with_suffix(".png"))

        plt.close(fig)
