import subprocess
from pathlib import Path

import cv2 as cv

from vvchelper.command import yuv2png
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

log = get_logger()

rootcfg = from_file(Path('pipeline.toml'))
cfg = rootcfg['pre']['dec2png']

src_dirs = path_from_root(rootcfg, rootcfg['pre']['codec']['dst'])
log.debug(f"src_dirs: {src_dirs}")
img_ref_dir = path_from_root(rootcfg, rootcfg['pre']['preprocess']['dst'])
dst_dirs = path_from_root(rootcfg, cfg['dst'])
log.debug(f"dst_dirs: {dst_dirs}")

for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name

    img_ref_path = next((img_ref_dir / seq_name).glob('*.png'))
    img_ref = cv.imread(str(img_ref_path))
    height, width = img_ref.shape[:2]

    for yuv_path in src_dir.glob('*.yuv'):
        log.debug(f"processing yuv: {yuv_path}")

        dst_dir = dst_dirs / seq_name / yuv_path.stem
        mkdir(dst_dir)

        cmds = yuv2png.build(
            rootcfg['app']['ffmpeg'],
            width,
            height,
            yuv_path,
            dst_dir / "frame#%03d.png",
        )
        subprocess.run(cmds)
