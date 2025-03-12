import json
import sys

from lvccc.config import update_config
from lvccc.helper import get_any_file, mkdir
from lvccc.logging import get_logger
from lvccc.task import CodecTask, Convert40Task, CopyTask, PostprocTask, PreprocTask, query
from lvccc.utils import CodecLog, calc_lenslet_psnr, calc_mv_psnr

config_fname = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
config = update_config(config_fname)

logger = get_logger()

summary_dir = config.dir.output / "summary/tasks"


for seq_name in config.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    # Anchor
    for qp in config.anchorQP.get(seq_name, []):
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
    offsetQP = config.proc.get("offsetQP", 0)
    for crop_size in config.proc["crop_size"].get(seq_name, []):
        tpreproc = PreprocTask(crop_size=crop_size).follow(tcopy)
        for anchorQP in config.anchorQP.get(seq_name, []):
            qp = anchorQP + offsetQP
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
