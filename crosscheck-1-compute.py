import json

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.logging import get_logger
from lvccc.task import (
    CodecTask,
    ComposeTask,
    CopyTask,
    Png2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2pngTask,
)
from lvccc.task.infomap import query
from lvccc.task.render import Pipeline
from lvccc.utils import lenslet_psnr, mv_psnr, read_enclog

name2pipeline = {
    "Boxer-IrishMan-Gladiator": Pipeline.RLC,
    "ChessPieces": Pipeline.RLC,
    "NagoyaFujita": Pipeline.RLC,
    "Boys": Pipeline.TLCT,
    "Matryoshka": Pipeline.TLCT,
}

config = update_config('config.toml')

log = get_logger()

summary_dir = config.path.output / 'summary/compute'


for seq_name in config.cases.seqs:
    # Anchor
    tcopy = CopyTask(seq_name=seq_name, frames=config.frames)

    trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tcopy)
    tcompose = ComposeTask().with_parent(trender)

    # W/O MCA
    tpng2yuv = Png2yuvTask().with_parent(tcopy)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.woMCA[seq_name]:
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
            tyuv2png = Yuv2pngTask().with_parent(tcodec)
            trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tyuv2png)
            tcompose = ComposeTask().with_parent(trender)

            if query(tcompose) is None:
                continue
            log.info(f"Handling {tcompose}")

            log_path = query(tcodec) / "out.log"
            enclog = read_enclog(log_path)

            llpsnr = lenslet_psnr(tcompose)
            mvpsnr = mv_psnr(tcompose)

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
                json.dump(metrics, f, indent=2)
            tcompose.dump_taskinfo(case_dir / "task.json")

    # W MCA
    tpreproc = PreprocTask().with_parent(tcopy)
    tpng2yuv = Png2yuvTask().with_parent(tpreproc)
    for vtm_type in config.cases.vtm_types:
        for qp in config.QP.wMCA[seq_name]:
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(tpng2yuv)
            tyuv2png = Yuv2pngTask().with_parent(tcodec)
            tpostproc = PostprocTask().with_parent(tyuv2png)
            trender = RenderTask(pipeline=name2pipeline[seq_name]).with_parent(tpostproc)
            tcompose = ComposeTask().with_parent(trender)

            if query(tcompose) is None:
                continue
            log.info(f"Handling {tcompose}")

            log_path = query(tcodec) / "out.log"
            enclog = read_enclog(log_path)

            mvpsnr = mv_psnr(tcompose)

            metrics = {
                'bitrate': enclog.bitrate,
                'mvpsnr_y': mvpsnr[0],
                'mvpsnr_u': mvpsnr[1],
                'mvpsnr_v': mvpsnr[2],
            }

            case_dir = summary_dir / tcodec.full_tag
            mkdir(case_dir)
            with (case_dir / "psnr.json").open('w') as f:
                json.dump(metrics, f, indent=2)
            tcompose.dump_taskinfo(case_dir / "task.json")
