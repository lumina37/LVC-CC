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
