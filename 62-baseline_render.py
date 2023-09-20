import subprocess
from pathlib import Path

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline.toml'))
render_cfg = cfg.baseline_render

for dataset_dir in cfg.dataset_root.iterdir():
    raytrix_cfg = RaytrixCfg.from_file(dataset_dir / render_cfg.param_file)
    raytrix_cfg.Calibration_xml = str(dataset_dir / render_cfg.calibration_file)
    raytrix_cfg.RawImage_Path = str(dataset_dir / render_cfg.src_dir / "%03d.png")
    raytrix_cfg.Output_Path = str(dataset_dir / render_cfg.dst_dir / "%03d")
    raytrix_cfg.to_file(dataset_dir / render_cfg.temp_param_file)

    print(f"Processing: {dataset_dir.name}")

    (dataset_dir / render_cfg.dst_dir).mkdir(0o755, parents=True, exist_ok=True)

    subprocess.run(
        [
            str(render_cfg.program),
            str(dataset_dir / render_cfg.temp_param_file),
        ]
    )
