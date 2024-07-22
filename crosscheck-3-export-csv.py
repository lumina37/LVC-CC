import csv
import dataclasses as dcs
import json

from lvccc.config import set_config
from lvccc.logging import get_logger


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
dst_dir = src_dir

with (dst_dir / "psnr.csv").open("w", encoding="utf-8", newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        [
            'seq-name',
            'QP - W/O MCA',
            'Bitrate',
            'Y-PSNR',
            'U-PSNR',
            'V-PSNR',
            'QP - W/ MCA',
            'Bitrate',
            'Y-PSNR',
            'U-PSNR',
            'V-PSNR',
        ]
    )

    for seq_name in config.cases.seqs:
        json_path = src_dir / f'{seq_name}.json'
        if not json_path.exists():
            continue

        with json_path.open() as f:
            seq_dic: dict = json.load(f)

        for vtm_type in config.cases.vtm_types:
            rows = [[seq_name] for _ in range(4)]
            for mca_type in ['woMCA', 'wMCA']:
                psnrs = [Stat(**d) for d in seq_dic[mca_type][vtm_type]]
                psnrs.sort(reverse=True)

                for rowidx, psnr in enumerate(psnrs):
                    rows[rowidx].extend([psnr.qp, psnr.bitrate, psnr.ypsnr, psnr.upsnr, psnr.vpsnr])

            csv_writer.writerows(rows)
