import argparse
import json
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import get_any_file, mkdir
from lvccc.logging import get_logger
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, query
from lvccc.utils import CodecLog, calc_lenslet_psnr, calc_mv_psnr

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
    anchorQPs = config.anchorQP.get(seq_name, None)
    if not anchorQPs:
        continue

    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    # Anchor
    for qp in anchorQPs:
        tcodec = CodecTask(qp=qp).follow(tcopy)
        tconvert = Convert40Task(views=config.views).follow(tcodec)

        if query(tconvert) is None:
            continue
        logger.info(f"Handling {tconvert.tag}")

        log_path = get_any_file(query(tcodec), "*.log")
        enclog = CodecLog.from_file(log_path)

        llpsnr = calc_lenslet_psnr(tconvert)
        mvpsnr = calc_mv_psnr(tconvert)

        metrics = {
            "bitrate": enclog.bitrate,
            "mvpsnr_y": mvpsnr[0],
            "mvpsnr_u": mvpsnr[1],
            "mvpsnr_v": mvpsnr[2],
            "llpsnr_y": llpsnr[0],
            "llpsnr_u": llpsnr[1],
            "llpsnr_v": llpsnr[2],
        }

        case_dir = summary_dir / tcodec.tag
        mkdir(case_dir)
        with (case_dir / "psnr.json").open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)
        tconvert.dump_taskinfo(case_dir / "task.json")

    # With Pre/Postprocess
    extendQP = config.proc.get("extendQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)
        for qp in range(anchorQPs[0] - extendQP, anchorQPs[-1]):
            tcodec = CodecTask(qp=qp).follow(tpreproc)
            tpostproc = PostprocTask().follow(tcodec)
            tconvert = Convert40Task(views=config.views).follow(tpostproc)

            if query(tconvert) is None:
                continue
            logger.info(f"Handling {tconvert.tag}")

            log_path = get_any_file(query(tcodec), "*.log")
            enclog = CodecLog.from_file(log_path)

            llpsnr = calc_lenslet_psnr(tconvert)
            mvpsnr = calc_mv_psnr(tconvert)

            metrics = {
                "bitrate": enclog.bitrate,
                "mvpsnr_y": mvpsnr[0],
                "mvpsnr_u": mvpsnr[1],
                "mvpsnr_v": mvpsnr[2],
                "llpsnr_y": llpsnr[0],
                "llpsnr_u": llpsnr[1],
                "llpsnr_v": llpsnr[2],
            }

            case_dir = summary_dir / tcodec.tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open("w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=4)
            tconvert.dump_taskinfo(case_dir / "task.json")
