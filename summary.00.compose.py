import subprocess

from mcahelper.command import png2yuv420
from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root, mkdir

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

base_src_dirs = get_root() / "playground/base/render"
dst_root = get_root() / "playground/summary/compose"

for seq_name in rootcfg['common']['seqs']:
    seq_name: str = seq_name

    log.debug(f"seq_name={seq_name}")

    base_src_dir = base_src_dirs / seq_name
    dst_dir = dst_root / seq_name / 'base'
    mkdir(dst_dir)
    view_count = len(list(next(base_src_dir.glob('frame#*')).glob('image*')))

    for view_idx in range(view_count):
        row_idx = (view_idx // 5) + 1
        col_idx = (view_idx % 5) + 1

        cmds = png2yuv420.build(
            base_src_dir / "frame#%03d" / f"image_{view_idx+1:0>3}.png",
            dst_dir / f"{row_idx}-{col_idx}.yuv",
        )
        subprocess.run(cmds)

for pre_type in ['wMCA', 'woMCA']:
    for vtm_type in rootcfg['common']['vtm_types']:
        vtm_type: str = vtm_type
        src_root = get_root() / "playground" / pre_type / "render" / vtm_type

        for seq_name in rootcfg['common']['seqs']:
            seq_name: str = seq_name

            src_dir = src_root / seq_name

            for qp in rootcfg['qp'][pre_type][seq_name]:
                log.debug(f"pre_type={pre_type}, vtm_type={vtm_type}, seq_name={seq_name}, QP={qp}")

                qp_str = f"QP#{qp}"
                qp_dir = src_dir / qp_str
                view_count = len(list(next(qp_dir.glob('frame#*')).glob('image*')))
                dst_dir = dst_root / seq_name / pre_type / vtm_type / qp_str
                mkdir(dst_dir)

                for view_idx in range(view_count):
                    row_idx = (view_idx // 5) + 1
                    col_idx = (view_idx % 5) + 1

                    cmds = png2yuv420.build(
                        qp_dir / "frame#%03d" / f"image_{view_idx+1:0>3}.png",
                        dst_dir / f"{row_idx}-{col_idx}.yuv",
                    )
                    subprocess.run(cmds)
