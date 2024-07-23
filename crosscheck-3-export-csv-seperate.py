import csv
import dataclasses as dcs
import json

from lvccc.config import update_config
from lvccc.logging import get_logger


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
            rows = [[seq_name] for _ in range(4)]
            for _, dic in [('woMCA', womca_dic), ('wMCA', wmca_dic)]:
                psnrs = [Stat(**d) for d in dic[vtm_type]]
                psnrs.sort(reverse=True)

                for rowidx, psnr in enumerate(psnrs):
                    rows[rowidx].extend([psnr.qp, psnr.bitrate, psnr.ypsnr, psnr.upsnr, psnr.vpsnr])

            csv_writer.writerows(rows)
