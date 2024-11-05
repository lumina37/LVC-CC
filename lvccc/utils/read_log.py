import dataclasses as dcs
import re
from io import TextIOBase


@dcs.dataclass
class EncLog:
    bitrate: float
    timecost: float


def read_enclog(logf: TextIOBase) -> EncLog:
    layerid_row_idx = -128

    for i, row in enumerate(logf):
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


def read_psnrlog(logf: TextIOBase) -> PSNR:
    def _get_psnr(s: str) -> float:
        _, psnr = s.split(':')
        return float(psnr)

    count = 0
    psnr = PSNR()
    for row in logf:
        sobj = re.search(r"y:[\d.]+ u:[\d.]+ v:[\d.]+", row)
        if not sobj:
            continue
        ypsnr_str, upsnr_str, vpsnr_str = sobj.group().rsplit(' ', maxsplit=2)
        psnr.y += _get_psnr(ypsnr_str)
        psnr.u += _get_psnr(upsnr_str)
        psnr.v += _get_psnr(vpsnr_str)
        count += 1

    psnr.y /= count
    psnr.u /= count
    psnr.v /= count

    return psnr
