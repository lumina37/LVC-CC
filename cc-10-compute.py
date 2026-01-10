import argparse
import json
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import get_any_file, mkdir
from lvccc.logging import get_logger
from lvccc.task import Convert45Task, CopyTask, DecodeTask, EncodeTask, query
from lvccc.utils import calc_lenslet_psnr, calc_mv_psnr

# Config from CMD
parser = argparse.ArgumentParser(description="Compute metrics of all tasks")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

logger = get_logger()


# Compute
summary_dir = config.dir.output / "summary/tasks"


for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    # Anchor
    for qp in config.anchorQP.get(seq_name, []):
        tenc = EncodeTask(qp=qp).follow(tcopy)
        tdec = DecodeTask().follow(tenc)
        tconvert = Convert45Task(views=config.views).follow(tdec)

        if query(tconvert) is None:
            continue

        case_dir = summary_dir / tenc.tag
        if (case_dir / "task.json").exists():
            continue

        logger.info(f"Handling {tconvert.tag}")

        bin_path = get_any_file(query(tenc), "*.bin")
        bin_size = bin_path.stat().st_size
        FPS = 30
        bitrate = bin_size * 8 / 1000 / (tconvert.frames / FPS)

        llpsnr = calc_lenslet_psnr(tconvert)
        mvpsnr = calc_mv_psnr(tconvert)

        metrics = {
            "bitrate": bitrate,
            "mvpsnr_y": mvpsnr[0],
            "mvpsnr_u": mvpsnr[1],
            "mvpsnr_v": mvpsnr[2],
            "llpsnr_y": llpsnr[0],
            "llpsnr_u": llpsnr[1],
            "llpsnr_v": llpsnr[2],
        }

        mkdir(case_dir)
        with (case_dir / "psnr.json").open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        tconvert.dump_taskinfo(case_dir / "task.json")
