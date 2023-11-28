import csv
import json

from mcahelper.config import set_rootcfg
from mcahelper.logging import get_logger
from mcahelper.utils import get_root

log = get_logger()

rootcfg = set_rootcfg('pipeline.toml')

tspc_names = ["Boys", "Cars", "Experimenting", "Matryoshka"]
tspc_vtm_map = {'randomaccess': 'RA', 'intra': 'INTRA'}

src_dir = get_root() / "playground/summary/compute"
tspc_src_dir = get_root() / "misc"
dst_dir = src_dir

with (src_dir / 'psnr.json').open('r') as f:
    main_dic: dict = json.load(f)

for vtm_type in rootcfg['common']['vtm_types']:
    dst_p = dst_dir / f'bitrate_ypsnr_11seqs_{vtm_type}.csv'
    with dst_p.open('w', encoding='utf-8', newline='') as csv_f:
        csv_writer = csv.writer(csv_f)
        headers = ['Seq.', 'Bitrate', 'Y-PSNR']
        csv_writer.writerow(headers)

        for seq_name, pre_type_dic in main_dic.items():
            vtm_dic = pre_type_dic['woMCA'][vtm_type]
            for i, (bitrate, ypsnr) in enumerate(zip(vtm_dic['bitrate'], vtm_dic['Y-PSNR'])):
                name = seq_name if i == 0 else ''
                row = [name, bitrate, ypsnr]
                csv_writer.writerow(row)

        for seq_name in tspc_names:
            tspc_p = tspc_src_dir / f'{seq_name}Cropped_VVC_{tspc_vtm_map[vtm_type]}PSNR.csv'
            with tspc_p.open('r', encoding='utf-8') as tspc_f:
                while row := tspc_f.readline():
                    if not row.startswith("All-Average"):
                        continue
                    _, bitrate, ypsnr, _ = row.rsplit(',', maxsplit=3)
                    csv_writer.writerow([seq_name, str(int(bitrate) / 125), ypsnr])
                    for _ in range(3):
                        row = tspc_f.readline()
                        _, bitrate, ypsnr, _ = row.rsplit(',', maxsplit=3)
                        csv_writer.writerow(['', str(int(bitrate) / 125), ypsnr])
