import dataclasses as dcs
import json

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from mcahelper.config import node
from mcahelper.logging import get_logger
from mcahelper.utils import mkdir

plt.rcParams['font.sans-serif'] = ['Times New Roman']


@dcs.dataclass
class Stat:
    bitrate: float
    qp: int
    ypsnr: float
    upsnr: float
    vpsnr: float

    def __lt__(self, rhs: "Stat") -> bool:
        return self.bitrate < rhs.bitrate


log = get_logger()

node_cfg = node.set_node_cfg('cfg-node.toml')

summary_dir = node_cfg.path.dataset / 'summary'
src_dir = summary_dir / 'compute'
dst_dir = summary_dir / 'figs'
mkdir(dst_dir)

mode_map = {'AI': 'All Intra', 'RA': 'Random Access'}

for seq_name in node_cfg.cases.seqs:
    with (src_dir / f'{seq_name}.json').open() as f:
        seq_dic: dict = json.load(f)

    for vtm_type in node_cfg.cases.vtm_types:
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
            psnrs = [Stat(**d) for d in seq_dic[tp][vtm_type]]
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
