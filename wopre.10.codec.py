import multiprocessing as mp
import subprocess
from pathlib import Path

from vvchelper.command import codec
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['wopre']['codec']

src_dir = path_from_root(rootcfg, rootcfg['wopre']['raw2yuv']['dst'])
dst_dirs = path_from_root(rootcfg, cfg['dst'])

ctcqp = {
    "Boxer-IrishMan-Gladiator": [37, 41, 45, 49],
    "chess": [37, 41, 45, 49],
    "ChessPieces": [33, 40, 45, 49],
    "NagoyaDataLeading": [38, 43, 49, 51],
    "NagoyaFujita": [36, 40, 45, 49],
    "NagoyaOrigami": [36, 40, 45, 49],
    "Tunnel_Train": [35, 40, 45, 49],
}

vtm_mode_cfg_path = path_from_root(rootcfg, rootcfg['config']['vtm_mode'])


def run(log_file: Path, args: list):
    with log_file.open('w') as f:
        subprocess.run(args, stdout=f, text=True)


def iter_args():
    for yuv_path in src_dir.glob('*.yuv'):
        seq_name = yuv_path.stem
        src_path = (src_dir / seq_name).with_suffix('.yuv')
        dst_dir = dst_dirs / seq_name
        mkdir(dst_dir)

        vtm_cfg_p = rootcfg['config']['vtm'].format(seq_name=seq_name)
        vtm_cfg_p = path_from_root(rootcfg, vtm_cfg_p)

        for qp in ctcqp[seq_name]:
            log.debug(f"processing seq: {seq_name}. QP={qp}")

            log_path = dst_dir / f'QP#{qp}.log'
            encoded_path = dst_dir / f'QP#{qp}.bin'
            decoded_path = dst_dir / f'QP#{qp}.yuv'

            cmds = codec.build(
                rootcfg['app']['encoder'],
                vtm_mode_cfg_path,
                vtm_cfg_p,
                qp,
                src_path,
                encoded_path,
                decoded_path,
            )
            yield (log_path, cmds)


if __name__ == "__main__":
    with mp.Pool(processes=cfg['parallel']) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
