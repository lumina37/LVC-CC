from __future__ import annotations

import dataclasses as dcs
import re
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from pathlib import Path


@dcs.dataclass
class CodecLog:
    bitrate: float
    timecost: float

    @staticmethod
    def load(f: TextIO) -> CodecLog:
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

        return CodecLog(bitrate, timecost)

    @staticmethod
    def from_file(path: Path) -> CodecLog:
        with path.open(encoding="utf-8") as f:
            return CodecLog.load(f)
