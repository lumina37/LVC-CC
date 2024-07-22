import dataclasses as dcs
import json

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import set_config
from lvccc.logging import get_logger
from lvccc.utils import mkdir

plt.rcParams['font.sans-serif'] = ['Times New Roman']


@dcs.dataclass
class Stat:
    bitrate: float
    qp: int
    ypsnr: float
    upsnr: float
    vpsnr: float
    ll_ypsnr: float = 0.0
    ll_upsnr: float = 0.0
    ll_vpsnr: float = 0.0

    def __lt__(self, rhs: "Stat") -> bool:
        return self.bitrate < rhs.bitrate


log = get_logger()

config = set_config('config.toml')

summary_dir = config.path.output / 'summary'
src_dir = summary_dir / 'compute'
dst_dir = summary_dir / 'figs'
mkdir(dst_dir)

for seq_name in config.cases.seqs:
    json_path = src_dir / f'{seq_name}.json'
    if not json_path.exists():
        continue

    with json_path.open() as f:
        seq_dic: dict = json.load(f)

    for vtm_type in config.cases.vtm_types:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = f'{seq_name}'
        ax.set_title(title)

        for tp, label, color in [
            ('wMCA', 'W/ MCA', 'orange'),
            ('woMCA', 'W/O MCA', 'blue'),
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
        fig.savefig((dst_dir / f'{seq_name}-{vtm_type}').with_suffix('.png'))
        fig.savefig((dst_dir / f'{seq_name}-{vtm_type}').with_suffix('.svg'))
