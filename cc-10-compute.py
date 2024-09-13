import json

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.logging import get_logger
from lvccc.task import (
    CodecTask,
    ComposeTask,
    Img2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2imgTask,
    YuvCopyTask,
    query,
)
from lvccc.utils import calc_lenslet_psnr, calc_mv_psnr, read_enclog

config = update_config('config.toml')

log = get_logger()

summary_dir = config.path.output / 'summary/tasks'


for seq_name in config.cases.seqs:
    tcopy = YuvCopyTask(seq_name=seq_name, frames=config.frames)

    # Anchor
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.anchor.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tcopy)
            tyuv2img = Yuv2imgTask().with_parent(tcodec)
            trender = RenderTask().with_parent(tyuv2img)
            tcompose = ComposeTask().with_parent(trender)

            if query(tcompose) is None:
                continue
            log.info(f"Handling {tcompose}")

            log_path = next(query(tcodec).glob('*.log'))
            enclog = read_enclog(log_path)

            llpsnr = calc_lenslet_psnr(tcompose)
            mvpsnr = calc_mv_psnr(tcompose)

            metrics = {
                'bitrate': enclog.bitrate,
                'mvpsnr_y': mvpsnr[0],
                'mvpsnr_u': mvpsnr[1],
                'mvpsnr_v': mvpsnr[2],
                'llpsnr_y': llpsnr[0],
                'llpsnr_u': llpsnr[1],
                'llpsnr_v': llpsnr[2],
            }

            case_dir = summary_dir / tcodec.full_tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open('w') as f:
                json.dump(metrics, f, indent=4)
            tcompose.dump_taskinfo(case_dir / "task.json")

    # W MCA
    tyuv2img = Yuv2imgTask().with_parent(tcopy)
    tpreproc = PreprocTask().with_parent(tyuv2img)
    timg2yuv = Img2yuvTask().with_parent(tpreproc)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.wMCA.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(timg2yuv)
            tyuv2img = Yuv2imgTask().with_parent(tcodec)
            tpostproc = PostprocTask().with_parent(tyuv2img)
            trender = RenderTask().with_parent(tpostproc)
            tcompose = ComposeTask().with_parent(trender)

            if query(tcompose) is None:
                continue
            log.info(f"Handling {tcompose}")

            log_path = next(query(tcodec).glob('*.log'))
            enclog = read_enclog(log_path)

            llpsnr = calc_lenslet_psnr(tcompose)
            mvpsnr = calc_mv_psnr(tcompose)

            metrics = {
                'bitrate': enclog.bitrate,
                'mvpsnr_y': mvpsnr[0],
                'mvpsnr_u': mvpsnr[1],
                'mvpsnr_v': mvpsnr[2],
                'llpsnr_y': llpsnr[0],
                'llpsnr_u': llpsnr[1],
                'llpsnr_v': llpsnr[2],
            }

            case_dir = summary_dir / tcodec.full_tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open('w') as f:
                json.dump(metrics, f, indent=4)
            tcompose.dump_taskinfo(case_dir / "task.json")
