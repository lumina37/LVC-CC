import json

from lvccc.config import update_config
from lvccc.helper import get_any_file, mkdir
from lvccc.logging import get_logger
from lvccc.task import CodecTask, ConvertTask, CopyTask, PostprocTask, PreprocTask, query
from lvccc.utils import calc_lenslet_psnr, calc_mv_psnr, read_enclog

config = update_config('config.toml')

log = get_logger()

summary_dir = config.path.output / 'summary/tasks'


for seq_name in config.cases.seqs:
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    # Anchor
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.anchor.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
            tconvert = ConvertTask(views=config.views).with_parent(tcodec)

            if query(tconvert) is None:
                continue
            log.info(f"Handling {tconvert.tag}")

            log_path = get_any_file(query(tcodec), '*.log')
            with log_path.open(encoding='utf-8') as logf:
                enclog = read_enclog(logf)

            llpsnr = calc_lenslet_psnr(tconvert)
            mvpsnr = calc_mv_psnr(tconvert)

            metrics = {
                'bitrate': enclog.bitrate,
                'mvpsnr_y': mvpsnr[0],
                'mvpsnr_u': mvpsnr[1],
                'mvpsnr_v': mvpsnr[2],
                'llpsnr_y': llpsnr[0],
                'llpsnr_u': llpsnr[1],
                'llpsnr_v': llpsnr[2],
            }

            case_dir = summary_dir / tcodec.tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open('w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=4)
            tconvert.dump_taskinfo(case_dir / "task.json")

    # W MCA
    tpreproc = PreprocTask().with_parent(tcopy)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.wMCA.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpreproc)
            tpostproc = PostprocTask().with_parent(tcodec)
            tconvert = ConvertTask(views=config.views).with_parent(tpostproc)

            if query(tconvert) is None:
                continue
            log.info(f"Handling {tconvert.tag}")

            log_path = get_any_file(query(tcodec), '*.log')
            enclog = read_enclog(log_path)

            llpsnr = calc_lenslet_psnr(tconvert)
            mvpsnr = calc_mv_psnr(tconvert)

            metrics = {
                'bitrate': enclog.bitrate,
                'mvpsnr_y': mvpsnr[0],
                'mvpsnr_u': mvpsnr[1],
                'mvpsnr_v': mvpsnr[2],
                'llpsnr_y': llpsnr[0],
                'llpsnr_u': llpsnr[1],
                'llpsnr_v': llpsnr[2],
            }

            case_dir = summary_dir / tcodec.tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open('w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=4)
            tconvert.dump_taskinfo(case_dir / "task.json")
