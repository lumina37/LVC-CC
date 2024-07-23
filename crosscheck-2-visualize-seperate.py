import dataclasses as dcs
import json

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
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

    def __lt__(self, rhs: "Stat") -> bool:
        return self.bitrate < rhs.bitrate


log = get_logger()

config = update_config('config.toml')

summary_dir = config.path.output / 'summary'
src_dir = summary_dir / 'compute'
dst_dir = summary_dir / 'figs'
mkdir(dst_dir)

for seq_name in config.cases.seqs:
    womca_json_path = src_dir / f'{seq_name}-woMCA.json'
    if not womca_json_path.exists():
        continue
    wmca_json_path = src_dir / f'{seq_name}-wMCA.json'
    if not wmca_json_path.exists():
        continue

    with womca_json_path.open(encoding='utf-8') as f:
        womca_dic: dict = json.load(f)
    with wmca_json_path.open(encoding='utf-8') as f:
        wmca_dic: dict = json.load(f)

    for vtm_type in config.cases.vtm_types:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = f'{seq_name}'
        ax.set_title(title)

        for _, dic, label, color in [
            ('wMCA', wmca_dic, 'W/ MCA', 'orange'),
            ('woMCA', womca_dic, 'W/O MCA', 'blue'),
        ]:
            psnrs = [Stat(**d) for d in dic[vtm_type]]
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
