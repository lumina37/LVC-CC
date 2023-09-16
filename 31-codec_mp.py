import multiprocessing as mp
import subprocess
from pathlib import Path

import cv2 as cv

from helper.configs.self import Cfg
from helper.configs.vtm import VTMCfg

cfg = Cfg.from_file(Path('pipeline.toml'))
codec_cfg = cfg.codec


def run(log_file: Path, args: list):
    with log_file.open('w') as f:
        subprocess.run(args, stdout=f, text=True)
        print(f"Finish with log: {log_file}")


def iter_args():
    for dataset_dir in cfg.dataset_root.iterdir():
        ref_img = cv.imread(str(dataset_dir / codec_cfg.size_ref_img_file))
        height, width = ref_img.shape[:2]

        vtm_cfg = VTMCfg.from_file(dataset_dir / codec_cfg.param_file)
        vtm_cfg.SourceHeight = height
        vtm_cfg.SourceWidth = width
        vtm_cfg.to_file(dataset_dir / codec_cfg.temp_param_file)

        for iqp in range(4):
            qp_start = 31
            qp_step = 5
            qp = qp_start + iqp * qp_step

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
                [
                    str(codec_cfg.program),
                    "-c",
                    str(codec_cfg.encode_mode_cfg_file),
                    "-c",
                    str(dataset_dir / codec_cfg.temp_param_file),
                    "-i",
                    str(dataset_dir / codec_cfg.src_file),
                    "-b",
                    dst_file_str,
                    "-o",
                    recon_file_str,
                    "--InternalBitDepth=8",
                    f"--QP={qp}",
                    "--FramesToBeEncoded=1",
                ],
            )


if __name__ == "__main__":
    with mp.Pool(processes=10) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
