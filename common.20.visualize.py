import re
from pathlib import Path
from typing import Dict, Tuple

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root


def get_bitrate(fp: Path) -> float:
    with fp.open('r') as f:
        layerid_row_idx = -128
        for i, row in enumerate(f.readlines()):
            if row.startswith('LayerId'):
                layerid_row_idx = i
            if i == layerid_row_idx + 2:
                num_strs = re.findall(r"\d+\.?\d*", row)
                bitrate_str = num_strs[1]
                return float(bitrate_str)


def get_QP2PSNR(fp: Path) -> Dict[int, int]:
    def get_QP_PSNR(row: str) -> Tuple[int, float]:
        res = row.rstrip('\n').split(',')
        _, qp, psnr = res
        return int(qp), float(psnr)

    dic = {}
    with fp.open('r') as f:
        while row := f.readline():
            if row.startswith('All-Average'):
                qp, psnr = get_QP_PSNR(row)
                dic[qp] = psnr
                break
        for _ in range(3):
            row = f.readline()
            qp, psnr = get_QP_PSNR(row)
            dic[qp] = psnr

    return dic


log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['common']['visualize']
psnr_dirs = path_from_root(rootcfg, rootcfg['common']['compute']['dst'])

suffix = "VVCPSNR.csv"
seq_names = [p.name.removesuffix(suffix) for p in (psnr_dirs / 'pre').iterdir()]

mkdir('figs')

for seq_name in seq_names:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax: Axes = ax
    ax.set_xlabel("Total bitrate (Kbps)")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title(seq_name)

    for tp, label, color in [
        ('wopre', 'W/O preprocess', 'orange'),
        ('pre', 'W preprocess', 'blue'),
    ]:
        psnr_fp = psnr_dirs / tp / f"{seq_name}{suffix}"
        qp2psnr = get_QP2PSNR(psnr_fp)

        codec = path_from_root(rootcfg, rootcfg[tp]['codec']['dst'])

        bitrates = []
        psnrs = []
        for qp, psnr in qp2psnr.items():
            render_log_fp = codec / seq_name / f"QP#{qp}.log"
            bitrate = get_bitrate(render_log_fp)
            bitrates.append(bitrate)
            psnrs.append(psnr)

        ax.plot(bitrates, psnrs, color=color, marker='o', label=label)

    ax.legend()
    fig.savefig(f"figs/{seq_name}.png")
    fig.savefig(f"figs/{seq_name}.svg")
