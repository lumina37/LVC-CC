import multiprocessing as mp
import subprocess

from mcahelper.command import render
from mcahelper.config import RaytrixCfg, set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "playground/woMCA/dec2png"
dst_dirs = get_root() / "playground/woMCA/render"


def run(args: list, log_str: str):
    subprocess.run(args)
    log.debug(f"Completed. {log_str}")


def iter_args():
    for vtm_type in rootcfg['common']['vtm_types']:
        vtm_type: str = vtm_type

        for seq_name in rootcfg['common']['seqs']:
            seq_name: str = seq_name

            for qp in rootcfg['qp']['woMCA'][seq_name]:
                log_str = f"vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}"

                qp_str = f"QP#{qp}"
                src_dir = dst_dirs / vtm_type / seq_name / qp_str
                dst_dir = dst_dirs / vtm_type / seq_name / qp_str
                mkdir(dst_dir)

                rlc_cfg_rpath = get_root() / "config" / seq_name / "rlc.cfg"
                rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rpath)

                rlc_cfg.Calibration_xml = str(rlc_cfg_rpath.with_name('calibration.xml'))
                rlc_cfg.RawImage_Path = str(src_dir / "frame#%03d.png")
                rlc_cfg.Output_Path = str(dst_dir / "frame#%03d")
                rlc_cfg.Isfiltering = 1
                rlc_cfg.end_frame = rootcfg['common']['frames']

                rlc_cfg_wpath = dst_dir / 'rlc.cfg'
                rlc_cfg.to_file(rlc_cfg_wpath)

                cmds = render.build(rlc_cfg_wpath)
                yield (cmds, log_str)


if __name__ == "__main__":
    with mp.Pool(processes=rootcfg['parallel']['woMCA']['render']) as pool:
        pool.starmap_async(run, iter_args())
        pool.close()
        pool.join()
