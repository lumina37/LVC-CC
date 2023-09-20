import subprocess
from pathlib import Path

import cv2 as cv

from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
dec2png_cfg = cfg.dec2png

for dataset_dir in cfg.dataset_root.iterdir():
    print(f"Processing: {dataset_dir.name}")

    ref_img = cv.imread(str(dataset_dir / dec2png_cfg.size_ref_img_file))
    height, width = ref_img.shape[:2]

    pattern = dataset_dir / dec2png_cfg.src_file_pattern
    for dec_file in pattern.parent.glob(pattern.name):
        dst_dir = dec2png_cfg.dst_dir_fstr.format(stem=dec_file.stem)
        (dataset_dir / dst_dir).mkdir(0o755, parents=True, exist_ok=True)

        subprocess.run(
            [
                str(cfg.ffmpeg),
                "-s",
                f"{width}x{height}",
                "-i",
                str(dec_file),
                str(dataset_dir / dst_dir / "%03d.png"),
                "-v",
                "warning",
            ]
        )
