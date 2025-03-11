import json
import sys

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, gen_infomap

config_fname = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
config = update_config(config_fname)

summary_dir = config.dir.output / "summary"
src_dir = summary_dir / "tasks"
dst_dir = summary_dir / "figure"
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)
    tpreproc = PreprocTask().with_parent(tcopy)

    for vtm_type in config.cases.vtm_types:
        anchor_bitrates = []
        anchor_psnrs = []
        for qp in config.anchorQP.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
            tconvert = Convert40Task(views=config.views).with_parent(tcodec)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                continue

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            anchor_bitrates.append(metrics["bitrate"])
            anchor_psnrs.append(metrics["mvpsnr_y"])

        proc_bitrates = []
        proc_psnrs = []
        for qp in config.proc["QP"].get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpreproc)
            tpostproc = PostprocTask().with_parent(tcodec)
            tconvert = Convert40Task(views=config.views).with_parent(tpostproc)

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
        title = f"{seq_name}"
        ax.set_title(title)

        ax.plot(anchor_bitrates, anchor_psnrs, label="anchor")
        ax.plot(proc_bitrates, proc_psnrs, label="proc")
        ax.legend()

        fname = f"{seq_name}-{vtm_type}"
        fig.savefig((dst_dir / fname).with_suffix(".png"))
        fig.savefig((dst_dir / fname).with_suffix(".svg"))
