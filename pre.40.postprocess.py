import math
import subprocess
from pathlib import Path

from vvchelper.command import postprocess
from vvchelper.config.raytrix import RaytrixCfg
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root

log = get_logger()

all_cfg = from_file(Path('pipeline.toml'))
cfg = all_cfg['pre']['postprocess']

src_dirs = path_from_root(all_cfg, all_cfg['pre']['dec2png']['dst'])
log.debug(f"src_dirs: {src_dirs}")
dst_dirs = path_from_root(all_cfg, cfg['dst'])
log.debug(f"dst_dirs: {dst_dirs}")

for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name

    seq_dir = dst_dirs / seq_name
    mkdir(seq_dir)

    rlc_cfg_rp = cfg['rlc_cfg'].format(seq_name=seq_name)
    rlc_cfg_rp = path_from_root(all_cfg, rlc_cfg_rp)
    rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rp)

    rlc_cfg.Calibration_xml = str(rlc_cfg_rp.with_name('calibration.xml'))
    rlc_cfg.square_width_diam_ratio = 1 / math.sqrt(2)

    rlc_cfg_wp = seq_dir / 'rlc.cfg'
    rlc_cfg.to_file(rlc_cfg_wp)

    for qp_dir in src_dir.iterdir():
        if not qp_dir.is_dir():
            continue

        log.debug(f"processing seq: {seq_name}. QP={get_QP(qp_dir.name)}")

        dst_dir = dst_dirs / seq_name / qp_dir.name
        mkdir(dst_dir)

        cmds = postprocess.build(
            all_cfg['program']['postprocess'],
            rlc_cfg_wp,
            qp_dir,
            dst_dir,
        )
        subprocess.run(cmds)
