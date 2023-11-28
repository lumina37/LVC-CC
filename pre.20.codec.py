import multiprocessing as mp
import subprocess
from pathlib import Path

import cv2 as cv

from mcahelper.command import codec
from mcahelper.config import VTMCfg, set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dir = get_root() / "playground/wMCA/wMCA2yuv"
dst_dirs = get_root() / "playground/wMCA/codec"
img_ref_dir = get_root() / "playground/wMCA/preproc"


def run(args: list, log_file: Path, log_str: str):
    with log_file.open('w') as f:
        subprocess.run(args, stdout=f, text=True)
    log.debug(f"Completed. {log_str}")


def iter_args():
    for vtm_type in rootcfg['common']['vtm_types']:
        vtm_type: str = vtm_type
        vtm_type_cfg_path = get_root() / f"config/encoder_{vtm_type}_vtm.cfg"

        for seq_name in rootcfg['common']['seqs']:
            seq_name: str = seq_name

            src_path = src_dir / f"{seq_name}.yuv"
            dst_dir = dst_dirs / vtm_type / seq_name
            mkdir(dst_dir)

            img_ref_path = next((img_ref_dir / seq_name).glob('*.png'))
            img_ref = cv.imread(str(img_ref_path))
            height, width = img_ref.shape[:2]

            vtm_cfg_rpath = get_root() / "config" / seq_name / "vtm.cfg"
            vtm_cfg = VTMCfg.from_file(vtm_cfg_rpath)
            vtm_cfg.SourceHeight = height
            vtm_cfg.SourceWidth = width

            vtm_cfg_wpath = dst_dir / 'vtm.cfg'
            vtm_cfg.to_file(vtm_cfg_wpath)

            for qp in rootcfg['qp']['wMCA'][seq_name]:
                log_str = f"vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}"

                qp_str = f"QP#{qp}"
                log_path = (dst_dir / qp_str).with_suffix('.log')
                encoded_path = (dst_dir / qp_str).with_suffix('.bin')
                decoded_path = (dst_dir / qp_str).with_suffix('.yuv')

                cmds = codec.build(
                    vtm_type_cfg_path,
                    vtm_cfg_wpath,
                    qp,
                    src_path,
                    encoded_path,
                    decoded_path,
                )
                yield (cmds, log_path, log_str)


if __name__ == "__main__":
    with mp.Pool(processes=rootcfg['parallel']['wMCA']['codec']) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
