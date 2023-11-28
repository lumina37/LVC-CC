import subprocess

from mcahelper.command import png2yuv420
from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, get_src_pattern, mkdir

log = get_logger()


rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "image"
dst_dir = get_root() / "playground/base/raw2yuv"
mkdir(dst_dir)


for src_dir in src_dirs.iterdir():
    if not src_dir.is_dir():
        continue

    seq_name = src_dir.name
    log.debug(f"processing seq: {seq_name}")

    fname_sample = next(src_dir.glob('*.png')).name

    cmds = png2yuv420.build(
        rootcfg['app']['ffmpeg'],
        src_dir / get_src_pattern(fname_sample),
        (dst_dir / seq_name).with_suffix('.yuv'),
    )
    subprocess.run(cmds)
