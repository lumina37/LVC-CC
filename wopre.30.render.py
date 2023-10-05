import multiprocessing as mp
import subprocess

from vvchelper.command import render
from vvchelper.config.raytrix import RaytrixCfg
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root

log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['wopre']['render']

src_dirs = path_from_root(rootcfg, rootcfg['wopre']['dec2png']['dst'])
dst_dirs = path_from_root(rootcfg, cfg['dst'])


def iter_args():
    for src_dir in src_dirs.iterdir():
        if not src_dir.is_dir():
            continue

        seq_name = src_dir.name
        if seq_name != 'chess':
            continue

        for qp_dir in src_dir.iterdir():
            if not qp_dir.is_dir():
                continue

            if get_QP(qp_dir.name) != 37:
                continue

            log.debug(f"processing seq: {seq_name}. QP={get_QP(qp_dir.name)}")

            dst_dir = dst_dirs / seq_name / qp_dir.name
            mkdir(dst_dir)

            rlc_cfg_rp = rootcfg['config']['rlc'].format(seq_name=seq_name)
            rlc_cfg_rp = path_from_root(rootcfg, rlc_cfg_rp)
            rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rp)

            rlc_cfg.Calibration_xml = str(rlc_cfg_rp.with_name('calibration.xml'))
            rlc_cfg.RawImage_Path = str(qp_dir / "frame#%03d.png")
            rlc_cfg.Output_Path = str(dst_dir / "frame#%03d")
            rlc_cfg.Isfiltering = 1
            rlc_cfg.end_frame = 30

            rlc_cfg_wp = dst_dir / 'rlc.cfg'
            rlc_cfg.to_file(rlc_cfg_wp)

            cmds = render.build(
                rootcfg['app']['rlc'],
                rlc_cfg_wp,
            )
            yield cmds


if __name__ == "__main__":
    with mp.Pool(processes=cfg['parallel']) as pool:
        pool.map_async(subprocess.run, iter_args())
        pool.close()
        pool.join()
