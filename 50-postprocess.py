import math
import random
import subprocess
from pathlib import Path

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
post_cfg = cfg.postprocess

for dataset_dir in cfg.dataset_root.iterdir():
    raytrix_cfg = RaytrixCfg.from_file(dataset_dir / post_cfg.param_file)
    for src_dir in (dataset_dir / post_cfg.src_dirs).iterdir():
        qp = int(src_dir.name)
        dst_dir_str = post_cfg.dst_dir_fstr.format(qp=qp)
        dst_dir = dataset_dir / dst_dir_str

        raytrix_cfg.Calibration_xml = str(dataset_dir / post_cfg.calibration_file)
        raytrix_cfg.square_width_diam_ratio = 1 / math.sqrt(2)

        tmpf = (dataset_dir / random.randbytes(4).hex()).with_suffix('.tmpcfg')
        raytrix_cfg.to_file(tmpf)

        print(f"Processing: {dataset_dir.name}")

        dst_dir.mkdir(0o755, parents=True, exist_ok=True)

        subprocess.run(
            [
                str(post_cfg.program),
                str(tmpf),
                str(src_dir),
                str(dst_dir),
            ]
        )

        tmpf.unlink()
