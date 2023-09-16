import math
import subprocess
from pathlib import Path

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
pre_cfg = cfg.preprocess

for dataset_dir in cfg.dataset_root.iterdir():
    raytrix_cfg = RaytrixCfg.from_file(dataset_dir / pre_cfg.param_file)
    raytrix_cfg.Calibration_xml = str(dataset_dir / pre_cfg.calibration_file)
    raytrix_cfg.square_width_diam_ratio = 1 / math.sqrt(2)
    raytrix_cfg.to_file(dataset_dir / pre_cfg.temp_param_file)

    print(f"Processing: {dataset_dir.name}")

    (dataset_dir / pre_cfg.dst_dir).mkdir(0o755, parents=True, exist_ok=True)

    subprocess.run(
        [
            str(pre_cfg.program),
            str(dataset_dir / pre_cfg.temp_param_file),
            str(dataset_dir / pre_cfg.src_dir),
            str(dataset_dir / pre_cfg.dst_dir),
        ]
    )
