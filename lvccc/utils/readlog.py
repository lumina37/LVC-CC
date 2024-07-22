import dataclasses as dcs
import re
from pathlib import Path


@dcs.dataclass
class EncLog:
    bitrate: float
    timecost: float


def read_enclog(path: Path) -> EncLog:
    with path.open(encoding='utf-8') as f:
        layerid_row_idx = -128

        for i, row in enumerate(f):
            if row.startswith("LayerId"):
                layerid_row_idx = i

            if layerid_row_idx > 0:
                if i == layerid_row_idx + 2:
                    matchobj = re.findall(r"\d+\.?\d*", row)
                    bitrate_str = matchobj[1]
                    bitrate = float(bitrate_str)
                    continue

                if i == layerid_row_idx + 5:
                    matchobj = re.search(r"Time:\s+(\d+\.?\d*)", row)
                    timecost_str = matchobj.group(1)
                    timecost = float(timecost_str)
                    continue

    log = EncLog(bitrate, timecost)
    return log


@dcs.dataclass
class PSNR:
    y: float = 0.0
    u: float = 0.0
    v: float = 0.0


def read_psnrlog(path: Path) -> PSNR:
    def _get_psnr(s: str) -> float:
        _, psnr = s.split(':')
        return float(psnr)

    count = 0
    psnr = PSNR()
    with path.open() as f:
        for row in f:
            row = row.rstrip('\n ')
            _, ypsnr_str, upsnr_str, vpsnr_str = row.rsplit(' ', maxsplit=3)
            psnr.y += _get_psnr(ypsnr_str)
            psnr.u += _get_psnr(upsnr_str)
            psnr.v += _get_psnr(vpsnr_str)
            count += 1

    psnr.y /= count
    psnr.u /= count
    psnr.v /= count

    return psnr
