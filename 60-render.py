import subprocess
from pathlib import Path

from helper.configs.raytrix import RaytrixCfg
from helper.configs.self import Cfg

cfg = Cfg.from_file(Path('pipeline_ref.toml'))
render_cfg = cfg.render

for dataset_dir in cfg.dataset_root.iterdir():
    for src_dir in (dataset_dir / render_cfg.src_dirs).iterdir():
        qp = int(src_dir.name)
        dst_dir_str = render_cfg.dst_dir_fstr.format(qp=qp)
        dst_dir = dataset_dir / dst_dir_str

        raytrix_cfg = RaytrixCfg.from_file(dataset_dir / render_cfg.param_file)
        raytrix_cfg.Calibration_xml = str(dataset_dir / render_cfg.calibration_file)
        raytrix_cfg.RawImage_Path = str(src_dir / "%03d.png")
        raytrix_cfg.Output_Path = str(dst_dir / "%03d")
        raytrix_cfg.to_file(dataset_dir / render_cfg.temp_param_file)

        print(f"Processing: {dataset_dir.name}")

        dst_dir.mkdir(0o755, parents=True, exist_ok=True)

        subprocess.run(
            [
                str(render_cfg.program),
                str(dataset_dir / render_cfg.temp_param_file),
            ]
        )

    break
