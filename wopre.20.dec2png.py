import subprocess

from mcahelper.command import yuv2png
from mcahelper.config import RaytrixCfg, set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "playground/woMCA/codec"
dst_dirs = get_root() / "playground/woMCA/dec2png"


for vtm_type in rootcfg['common']['vtm_types']:
    vtm_type: str = vtm_type

    for seq_name in rootcfg['common']['seqs']:
        seq_name: str = seq_name
        log.debug(f"seq_name={seq_name}")

        rlc_cfg_rpath = get_root() / "config" / seq_name / "rlc.cfg"
        rlc_cfg = RaytrixCfg.from_file(rlc_cfg_rpath)
        width = rlc_cfg.width
        height = rlc_cfg.height

        for qp in rootcfg['qp']['woMCA'][seq_name]:
            log.debug(f"vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}")

            yuv_path = src_dirs / vtm_type / seq_name / f"QP#{qp}.yuv"
            dst_dir = dst_dirs / vtm_type / seq_name / yuv_path.stem
            mkdir(dst_dir)

            cmds = yuv2png.build(
                width,
                height,
                yuv_path,
                dst_dir / "frame#%03d.png",
            )
            subprocess.run(cmds)
