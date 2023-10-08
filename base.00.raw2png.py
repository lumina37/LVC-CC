import subprocess
from pathlib import Path

from vvchelper.command import yuv2png
from vvchelper.config.raytrix import RaytrixCfg
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

log = get_logger()

rootcfg = from_file(Path('pipeline.toml'))
cfg = rootcfg['base']['raw2png']

src_dir = path_from_root(rootcfg, rootcfg['wopre']['raw2yuv']['dst'])
log.debug(f"src_dir: {src_dir}")
dst_dirs = path_from_root(rootcfg, cfg['dst'])
log.debug(f"dst_dirs: {dst_dirs}")

for yuv_path in src_dir.glob('*.yuv'):
    seq_name = yuv_path.stem
    log.debug(f"processing seq: {seq_name}")

    rlc_cfg_p = rootcfg['config']['rlc'].format(seq_name=seq_name)
    rlc_cfg_p = path_from_root(rootcfg, rlc_cfg_p)
    raytrix_cfg = RaytrixCfg.from_file(rlc_cfg_p)
    width = raytrix_cfg.width
    height = raytrix_cfg.height

    dst_dir = dst_dirs / seq_name
    mkdir(dst_dir)

    cmds = yuv2png.build(
        rootcfg['app']['ffmpeg'],
        rootcfg['frames'],
        width,
        height,
        yuv_path,
        dst_dir / "frame#%03d.png",
    )
    subprocess.run(cmds)
