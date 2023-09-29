import multiprocessing as mp
import subprocess
from pathlib import Path

import cv2 as cv

from vvchelper.command import codec
from vvchelper.config.self import from_file
from vvchelper.config.vtm import VTMCfg
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

log = get_logger()

all_cfg = from_file('pipeline.toml')
cfg = all_cfg['pre']['codec']

src_dir = path_from_root(all_cfg, all_cfg['pre']['pre2yuv']['dst'])
img_ref_dir = path_from_root(all_cfg, all_cfg['pre']['preprocess']['dst'])
dst_dirs = path_from_root(all_cfg, cfg['dst'])

ctcqp = {
    "Boxer-IrishMan-Gladiator": [33, 37, 41, 45],
    "chess": [32, 37, 41, 45],
    "ChessPieces": [30, 33, 40, 45],
    "NagoyaDataLeading": [33, 38, 43, 49],
    "NagoyaFujita": [32, 36, 40, 45],
    "NagoyaOrigami": [31, 36, 40, 45],
    "Tunnel_Train": [30, 35, 40, 45],
}

vtm_intra_cfg_path = path_from_root(all_cfg, "./config/encoder_intra_vtm.cfg")


def run(log_file: Path, args: list):
    with log_file.open('w') as f:
        subprocess.run(args, stdout=f, text=True)


def iter_args():
    for yuv_path in src_dir.glob('*.yuv'):
        seq_name = yuv_path.stem

        src_path = (src_dir / seq_name).with_suffix('.yuv')
        dst_dir = dst_dirs / seq_name
        mkdir(dst_dir)

        img_ref_path = next((img_ref_dir / seq_name).glob('*.png'))
        img_ref = cv.imread(str(img_ref_path))
        height, width = img_ref.shape[:2]

        vtm_cfg_rp = cfg['vtm_cfg'].format(seq_name=seq_name)
        vtm_cfg_rp = path_from_root(all_cfg, vtm_cfg_rp)

        vtm_cfg = VTMCfg.from_file(vtm_cfg_rp)
        vtm_cfg.SourceHeight = height
        vtm_cfg.SourceWidth = width

        vtm_cfg_wp = dst_dir / 'vtm.cfg'
        vtm_cfg.to_file(vtm_cfg_wp)

        for qp in ctcqp[seq_name]:
            log.debug(f"processing seq: {seq_name}. QP={qp}")

            log_path = dst_dir / f'QP#{qp}.log'
            encoded_path = dst_dir / f'QP#{qp}.bin'
            decoded_path = dst_dir / f'QP#{qp}.yuv'

            cmds = codec.build(
                all_cfg['program']['encoder'],
                vtm_intra_cfg_path,
                vtm_cfg_wp,
                qp,
                src_path,
                encoded_path,
                decoded_path,
            )
            yield (log_path, cmds)


if __name__ == "__main__":
    with mp.Pool(processes=12) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
