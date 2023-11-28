import math
import subprocess

from mcahelper.command import postproc
from mcahelper.config import RaytrixCfg, set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "playground/wMCA/dec2png"
dst_dirs = get_root() / "playground/wMCA/postproc"

for vtm_type in rootcfg['common']['vtm_types']:
    vtm_type: str = vtm_type

    for seq_name in rootcfg['common']['seqs']:
        seq_name: str = seq_name

        dst_dir = dst_dirs / vtm_type / seq_name
        mkdir(dst_dir)

        rlc_cfg_rpath = get_root() / "config" / seq_name / "rlc.cfg"
        rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rpath)

        rlc_cfg.Calibration_xml = str(rlc_cfg_rpath.with_name('calibration.xml'))
        rlc_cfg.square_width_diam_ratio = 1 / math.sqrt(2)

        rlc_cfg_wp = dst_dir / 'rlc.cfg'
        rlc_cfg.to_file(rlc_cfg_wp)

        for qp in rootcfg['qp']['wMCA'][seq_name]:
            log.debug(f"processing seq: {seq_name}. QP={qp}")

            qp_str = f"QP#{qp}"
            src_dir = src_dirs / vtm_type / seq_name / qp_str
            dst_dir = dst_dirs / vtm_type / seq_name / qp_str
            mkdir(dst_dir)

            cmds = postproc.build(
                rlc_cfg_wp,
                src_dir,
                dst_dir,
            )
            subprocess.run(cmds)
