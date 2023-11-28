import subprocess

import cv2 as cv

from mcahelper.command import yuv2png
from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "playground/wMCA/codec"
dst_dirs = get_root() / "playground/wMCA/dec2png"
img_ref_dir = get_root() / "playground/wMCA/preproc"

for vtm_type in rootcfg['common']['vtm_types']:
    vtm_type: str = vtm_type

    for seq_name in rootcfg['common']['seqs']:
        seq_name: str = seq_name

        src_path = src_dirs / f"{seq_name}.yuv"

        img_ref_path = next((img_ref_dir / seq_name).glob('*.png'))
        img_ref = cv.imread(str(img_ref_path))
        height, width = img_ref.shape[:2]

        for qp in rootcfg['qp']['wMCA'][seq_name]:
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
