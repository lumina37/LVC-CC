import subprocess

from mcahelper.command import png2yuv420
from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, get_src_pattern, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

src_dirs = get_root() / "playground/wMCA/preproc"
dst_dir = get_root() / "playground/wMCA/wMCA2yuv"
mkdir(dst_dir)

for seq_name in rootcfg['common']['seqs']:
    seq_name: str = seq_name
    log.debug(f"seq_name={seq_name}")

    src_dir = src_dirs / seq_name
    fname_sample = next(src_dir.glob('*.png')).name

    cmds = png2yuv420.build(
        src_dir / get_src_pattern(fname_sample),
        (dst_dir / seq_name).with_suffix('.yuv'),
    )
    subprocess.run(cmds)
