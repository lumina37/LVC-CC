import json
from typing import Dict

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from vvchelper.config.self import from_file
from vvchelper.logging import get_logger
from vvchelper.utils import mkdir, path_from_root

plt.rcParams['font.sans-serif'] = ['Times New Roman']

log = get_logger()

rootcfg = from_file('pipeline.toml')
cfg = rootcfg['common']['visualize']
src_dir = path_from_root(rootcfg, rootcfg['common']['compute']['dst'])

dst_dir = path_from_root(rootcfg, cfg['dst'])
mkdir(dst_dir)

with (src_dir / 'psnr.json').open('r') as f:
    main_dic: Dict[str, dict] = json.load(f)


for seq_name, seq_dic in main_dic.items():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax: Axes = ax
    ax.set_xlabel("Total bitrate (Kbps)")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title(seq_name)

    for tp, label, color in [
        ('wopre', 'W/O preprocess', 'orange'),
        ('pre', 'W/ preprocess', 'blue'),
    ]:
        ax.plot(seq_dic[tp]['bitrate'], seq_dic[tp]['Y-PSNR'], color=color, marker='o', label=label)

    ax.legend()
    fig.savefig((dst_dir / seq_name).with_suffix('.png'))
    fig.savefig((dst_dir / seq_name).with_suffix('.svg'))
