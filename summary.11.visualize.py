import dataclasses as dcs
import json
from typing import Dict

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from mcahelper.cfg import node
from mcahelper.logging import get_logger
from mcahelper.utils import mkdir

plt.rcParams['font.sans-serif'] = ['Times New Roman']


@dcs.dataclass
class PSNR:
    bitrate: float
    qp: int
    ypsnr: float
    upsnr: float
    vpsnr: float

    def __lt__(self, rhs: "PSNR") -> bool:
        return self.bitrate < rhs.bitrate


log = get_logger()

rootcfg = node.set_node_cfg('node-cfg.toml')

src_dir = rootcfg.path.dataset / 'summary'
dst_dir = src_dir / 'figs'
mkdir(dst_dir)

with (src_dir / 'psnr.json').open('r') as f:
    main_dic: Dict[str, dict] = json.load(f)


mode_map = {'AI': 'All Intra', 'RA': 'Random Access'}

for seq_name, seq_dic in main_dic.items():
    for vtm_type in rootcfg.cases.vtm_types:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = f'{seq_name}, config: {mode_map[vtm_type]}'
        ax.set_title(title)

        for tp, label, color in [
            ('wMCA', 'W/O MCA', 'orange'),
            ('woMCA', 'W/ MCA', 'blue'),
        ]:
            psnrs = [PSNR(**d) for d in seq_dic[tp][vtm_type]]
            psnrs.sort()
            ax.plot(
                [p.bitrate for p in psnrs],
                [p.ypsnr for p in psnrs],
                color=color,
                marker='o',
                label=label,
            )

        ax.legend()
        fig.savefig((dst_dir / f'{seq_name}_{vtm_type}').with_suffix('.png'))
        fig.savefig((dst_dir / f'{seq_name}_{vtm_type}').with_suffix('.svg'))
