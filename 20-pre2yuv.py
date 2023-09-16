import subprocess
from pathlib import Path

import cv2 as cv

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
pre2yuv_cfg = cfg.pre2yuv

for dataset_dir in cfg.dataset_root.iterdir():
    raytrix_cfg = RaytrixCfg.from_file(dataset_dir / pre2yuv_cfg.param_file)

    print(f"Processing: {dataset_dir.name}")

    ref_img = cv.imread(str(dataset_dir / pre2yuv_cfg.src_dir / "001.png"))
    height, width = ref_img.shape[:2]

    subprocess.run(
        [
            str(cfg.ffmpeg),
            "-v",
            "warning",
            "-r",
            "30",
            "-i",
            str(dataset_dir / pre2yuv_cfg.src_dir / "%03d.png"),
            "-pix_fmt",
            "yuv420p",
            str(dataset_dir / pre2yuv_cfg.dst_file),
            "-y",
        ]
    )
