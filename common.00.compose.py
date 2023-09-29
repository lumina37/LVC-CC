import subprocess

from vvchelper.command import png2yuv420
from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import get_QP, mkdir, path_from_root

log = get_logger()

all_cfg = from_file('pipeline.toml')
cfg = all_cfg['common']['compose']
base_src_dirs = path_from_root(all_cfg, all_cfg['base']['render']['dst'])
dst_root = path_from_root(all_cfg, cfg['dst'])

for base_src_dir in base_src_dirs.iterdir():
    if not base_src_dir.is_dir():
        continue

    seq_name = base_src_dir.name

    log.debug(f"processing base seq: {seq_name}")

    view_count = len(list(next(base_src_dir.glob('frame#*')).glob('image*')))
    dst_dir = dst_root / 'base' / f"{seq_name}_Ref_MV_YUV"
    mkdir(dst_dir)

    for view_idx in range(view_count):
        row_idx = (view_idx // 5) + 1
        col_idx = (view_idx % 5) + 1

        cmds = png2yuv420.build(
            all_cfg['program']['ffmpeg'],
            base_src_dir / "frame#%03d" / f"image_{view_idx+1:0>3}.png",
            dst_dir / f"MV_{row_idx}_{col_idx}.yuv",
        )
        subprocess.run(cmds)

wopre_src_dirs = path_from_root(all_cfg, all_cfg['wopre']['render']['dst'])
for wopre_src_dir in wopre_src_dirs.iterdir():
    if not wopre_src_dir.is_dir():
        continue

    seq_name = wopre_src_dir.name

    for qp_str in wopre_src_dir.iterdir():
        if not qp_str.is_dir():
            continue

        qp = get_QP(qp_str.name)
        log.debug(f"processing wopre seq: {seq_name}. QP={qp}")

        view_count = len(list(next(qp_str.glob('frame#*')).glob('image*')))
        dst_dir = dst_root / 'wopre' / seq_name / "VVC" / str(qp) / "MV_YUV"
        mkdir(dst_dir)

        for view_idx in range(view_count):
            row_idx = (view_idx // 5) + 1
            col_idx = (view_idx % 5) + 1

            cmds = png2yuv420.build(
                all_cfg['program']['ffmpeg'],
                wopre_src_dir / qp_str.name / "frame#%03d" / f"image_{view_idx+1:0>3}.png",
                dst_dir / f"Rec_MV_{row_idx}_{col_idx}.yuv",
            )
            subprocess.run(cmds)

pre_src_dirs = path_from_root(all_cfg, all_cfg['pre']['render']['dst'])
for pre_src_dir in pre_src_dirs.iterdir():
    if not pre_src_dir.is_dir():
        continue

    seq_name = pre_src_dir.name

    for qp_str in pre_src_dir.iterdir():
        if not qp_str.is_dir():
            continue

        qp = get_QP(qp_str.name)
        log.debug(f"processing pre seq: {seq_name}. QP={qp}")

        view_count = len(list(next(qp_str.glob('frame#*')).glob('image*')))
        dst_dir = dst_root / 'pre' / seq_name / "VVC" / str(qp) / "MV_YUV"
        mkdir(dst_dir)

        for view_idx in range(view_count):
            row_idx = (view_idx // 5) + 1
            col_idx = (view_idx % 5) + 1

            cmds = png2yuv420.build(
                all_cfg['program']['ffmpeg'],
                pre_src_dir / qp_str.name / "frame#%03d" / f"image_{view_idx+1:0>3}.png",
                dst_dir / f"Rec_MV_{row_idx}_{col_idx}.yuv",
            )
            subprocess.run(cmds)
