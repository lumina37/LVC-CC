import subprocess
from pathlib import Path

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
raw2png_cfg = cfg.raw2png

for dataset_dir in cfg.dataset_root.iterdir():
    raytrix_cfg = RaytrixCfg.from_file(dataset_dir / raw2png_cfg.param_file)

    print(f"Processing: {dataset_dir.name}")

    (dataset_dir / raw2png_cfg.dst_dir).mkdir(0o755, parents=True, exist_ok=True)

    subprocess.run(
        [
            str(cfg.ffmpeg),
            "-s",
            f"{raytrix_cfg.width}x{raytrix_cfg.height}",
            "-i",
            str(dataset_dir / raw2png_cfg.src_file),
            str(dataset_dir / raw2png_cfg.dst_dir / "%03d.png"),
            "-v",
            "warning",
        ]
    )
