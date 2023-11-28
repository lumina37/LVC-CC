import math
import subprocess

from mcahelper.command import preproc
from mcahelper.config import RaytrixCfg, set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "image"
dst_dirs = get_root() / "playground/wMCA/preproc"

for seq_name in rootcfg['common']['seqs']:
    seq_name: str = seq_name
    log.debug(f"seq_name={seq_name}")

    src_dir = src_dirs / seq_name
    dst_dir = dst_dirs / seq_name
    mkdir(dst_dir)

    rlc_cfg_rpath = get_root() / "config" / seq_name / "rlc.cfg"
    rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rpath)

    rlc_cfg.Calibration_xml = str(rlc_cfg_rpath.with_name('calibration.xml'))
    rlc_cfg.square_width_diam_ratio = 1 / math.sqrt(2)

    rlc_cfg_wpath = dst_dir / "rlc.cfg"
    rlc_cfg.to_file(rlc_cfg_wpath)

    cmds = preproc.build(
        rlc_cfg_wpath,
        src_dir,
        dst_dir,
    )
    subprocess.run(cmds)
