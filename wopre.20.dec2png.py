import subprocess
from pathlib import Path

from vvchelper.command import yuv2png
from vvchelper.config.raytrix import RaytrixCfg
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

log = get_logger()

rootcfg = from_file(Path('pipeline.toml'))
cfg = rootcfg['wopre']['dec2png']

src_dirs = path_from_root(rootcfg, rootcfg['wopre']['codec']['dst'])
log.debug(f"src_dirs: {src_dirs}")
dst_dirs = path_from_root(rootcfg, cfg['dst'])
log.debug(f"dst_dirs: {dst_dirs}")

for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name

    rlc_cfg_p = rootcfg['config']['rlc'].format(seq_name=seq_name)
    rlc_cfg_p = path_from_root(rootcfg, rlc_cfg_p)
    raytrix_cfg = RaytrixCfg.from_file(rlc_cfg_p)

    width = raytrix_cfg.width
    height = raytrix_cfg.height

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
