import json

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, ConvertTask, CopyTask, gen_infomap

config = update_config("config.toml")

summary_dir = config.path.output / "summary"
src_dir = summary_dir / "tasks"
dst_dir = summary_dir / "figure"
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    for vtm_type in config.cases.vtm_types:
        bitrates = []
        psnrs = []

        for qp in config.QP.anchor.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
            tconvert = ConvertTask(views=config.views).with_parent(tcodec)

            json_path = src_dir / tcodec.tag / "psnr.json"
            if not json_path.exists():
                continue

            with json_path.open(encoding="utf-8") as f:
                metrics: dict = json.load(f)

            bitrates.append(metrics["bitrate"])
            psnrs.append(metrics["mvpsnr_y"])

        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = f"{seq_name}"
        ax.set_title(title)

        ax.plot(bitrates, psnrs)

        label = "anchor"
        fname = f"{label}-{seq_name}-{vtm_type}"
        fig.savefig((dst_dir / fname).with_suffix(".png"))
        fig.savefig((dst_dir / fname).with_suffix(".svg"))
