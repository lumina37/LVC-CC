import multiprocessing as mp
import subprocess
from pathlib import Path

from mcahelper.command import codec
from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dir = get_root() / "playground/base/raw2yuv"
dst_dirs = get_root() / "playground/woMCA/codec"


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

            vtm_cfg_path = get_root() / "config" / seq_name / "vtm.cfg"

            for qp in rootcfg['qp']['woMCA'][seq_name]:
                log_str = f"vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}"

                qp_str = f"QP#{qp}"
                log_path = (dst_dir / qp_str).with_suffix('.log')
                encoded_path = (dst_dir / qp_str).with_suffix('.bin')
                decoded_path = (dst_dir / qp_str).with_suffix('.yuv')

                cmds = codec.build(
                    vtm_type_cfg_path,
                    vtm_cfg_path,
                    qp,
                    src_path,
                    encoded_path,
                    decoded_path,
                )
                yield (cmds, log_path, log_str)


if __name__ == "__main__":
    with mp.Pool(processes=rootcfg['parallel']['woMCA']['codec']) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
