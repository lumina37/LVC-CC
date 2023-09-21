import atexit
import random
import subprocess
from pathlib import Path

import cv2 as cv

from helper.configs.self import Cfg
from helper.configs.vtm import VTMCfg


def run(log_file: Path, args: list):
    with log_file.open('w') as f:
        subprocess.run(args, stdout=f, text=True)
        print(f"Finish with log: {log_file}")


def iter_args(cfg: Cfg):
    codec_cfg = cfg.codec

    for dataset_dir in cfg.dataset_root.iterdir():
        ref_img = cv.imread(str(dataset_dir / codec_cfg.size_ref_img_file))
        height, width = ref_img.shape[:2]

        vtm_cfg = VTMCfg.from_file(dataset_dir / codec_cfg.param_file)
        vtm_cfg.SourceHeight = height
        vtm_cfg.SourceWidth = width

        tmpf = dataset_dir / random.randbytes(4).hex()
        vtm_cfg.to_file(tmpf)
        atexit.register(tmpf.unlink)

        for qp in codec_cfg.ctcqp[dataset_dir.name]:

            def fmt_and_mkdir(fp_fstr: str) -> str:
                fp_str = fp_fstr.format(qp=qp)
                fp = dataset_dir / fp_str
                fp.parent.mkdir(0o755, parents=True, exist_ok=True)
                return str(fp)

            dst_file_str = fmt_and_mkdir(codec_cfg.dst_file_fstr)
            log_file_str = fmt_and_mkdir(codec_cfg.log_file_fstr)
            recon_file_str = fmt_and_mkdir(codec_cfg.recon_file_fstr)

            yield (
                dataset_dir / log_file_str,
                tmpf,
                [
                    str(codec_cfg.program),
                    "-c",
                    str(codec_cfg.encode_mode_cfg_file),
                    "-c",
                    str(tmpf),
                    "--InternalBitDepth=8",
                    "--FramesToBeEncoded=5",
                    "--TemporalSubsampleRatio=1",
                    f"--QP={qp}",
                    "-i",
                    str(dataset_dir / codec_cfg.src_file),
                    "-b",
                    dst_file_str,
                    "-o",
                    recon_file_str,
                ],
            )
