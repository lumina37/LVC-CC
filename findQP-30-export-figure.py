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

    anchorQPs = config.anchorQP.get(seq_name, None)
    if not anchorQPs:
        continue

    anchor_bitrates = []
    anchor_mvpsnrs = []
    anchor_llpsnrs = []
    for qp in anchorQPs:
        tcodec = CodecTask(qp=qp).follow(tcopy)
        tconvert = Convert40Task(views=config.views).follow(tcodec)

        json_path = src_dir / tcodec.tag / "psnr.json"
        if not json_path.exists():
            continue

        with json_path.open(encoding="utf-8") as f:
            metrics: dict = json.load(f)

        anchor_bitrates.append(metrics["bitrate"])
        anchor_mvpsnrs.append(metrics["mvpsnr_y"])
        anchor_llpsnrs.append(metrics["llpsnr_y"])

    extendQP = config.proc.get("extendQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)

        proc_bitrates = []
        proc_mvpsnrs = []
        proc_llpsnrs = []
        procQPs = []
        for qp in range(anchorQPs[0] - extendQP, anchorQPs[-1] + 1):
            tcodec = CodecTask(qp=qp).follow(tpreproc)
            tpostproc = PostprocTask().follow(tcodec)
            tconvert = Convert40Task(views=config.views).follow(tpostproc)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                continue

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            proc_bitrates.append(metrics["bitrate"])
            proc_mvpsnrs.append(metrics["mvpsnr_y"])
            proc_llpsnrs.append(metrics["llpsnr_y"])
            procQPs.append(qp)

        # Multi-view
        mvfig, mvax = plt.subplots(figsize=(6, 6))
        mvax: Axes = mvax
        mvax.set_xlabel("Total bitrate (Kbps)")
        mvax.set_ylabel("Multi-view PSNR (dB)")
        mvtitle = f"{tpreproc.tag}-multiview"
        mvax.set_title(mvtitle)

        mvax.plot(anchor_bitrates, anchor_mvpsnrs, label="anchor", color="blue", marker="o", markersize=1)
        for i in range(len(anchor_bitrates)):
            mvax.annotate(str(anchorQPs[i]), xy=(anchor_bitrates[i], anchor_mvpsnrs[i]), color="blue")

        mvax.plot(proc_bitrates, proc_mvpsnrs, label="proc", color="orange", marker="o", markersize=1)
        for i in range(len(proc_bitrates)):
            mvax.annotate(str(procQPs[i]), xy=(proc_bitrates[i], proc_mvpsnrs[i]), color="orange")

        mvax.legend()

        mvfig.savefig((dst_dir / mvtitle).with_suffix(".png"))

        plt.close(mvfig)

        # Multi-view
        llfig, llax = plt.subplots(figsize=(6, 6))
        llax: Axes = llax
        llax.set_xlabel("Total bitrate (Kbps)")
        llax.set_ylabel("Lenslet PSNR (dB)")
        lltitle = f"{tpreproc.tag}-lenslet"
        llax.set_title(lltitle)

        llax.plot(anchor_bitrates, anchor_llpsnrs, label="anchor", color="blue", marker="o", markersize=1)
        for i in range(len(anchor_bitrates)):
            llax.annotate(str(anchorQPs[i]), xy=(anchor_bitrates[i], anchor_llpsnrs[i]), color="blue")

        llax.plot(proc_bitrates, proc_llpsnrs, label="proc", color="orange", marker="o", markersize=1)
        for i in range(len(proc_bitrates)):
            llax.annotate(str(procQPs[i]), xy=(proc_bitrates[i], proc_llpsnrs[i]), color="orange")

        llax.legend()

        llfig.savefig((dst_dir / lltitle).with_suffix(".png"))

        plt.close(llfig)
