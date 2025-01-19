import csv
import json
import sys

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import CodecTask, Convert40Task, CopyTask, gen_infomap

config_fname = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
config = update_config(config_fname)

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
        "Bitrate",
        "LLPSNR-Y",
        "LLPSNR-U",
        "LLPSNR-V",
        "MVPSNR-Y",
        "MVPSNR-U",
        "MVPSNR-V",
    ]
    csv_writer.writerow(headers)

    for seq_name in config.cases.seqs:
        tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

        for vtm_type in config.cases.vtm_types:
            for qp in config.QP.anchor.get(seq_name, []):
                tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
                tconvert = Convert40Task(views=config.views).with_parent(tcodec)

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
