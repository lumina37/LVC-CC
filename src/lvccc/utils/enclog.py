from __future__ import annotations

import dataclasses as dcs
import re
from typing import TYPE_CHECKING, TextIO

from ..logging import get_logger

if TYPE_CHECKING:
    from pathlib import Path


@dcs.dataclass
class EncodeLog:
    bitrate: float = 0.0
    timecost: float = 0.0

    @staticmethod
    def load(f: TextIO) -> EncodeLog:
        is_completed = False
        for row in f:
            if row.startswith("LayerId"):
                is_completed = True
                break
        if not is_completed:
            logger = get_logger()
            logger.warning(f"The codec log is incomplete: name={f.name}")
            return EncodeLog()

        f.readline()  # skip the table header

        matchobj = re.findall(r"\d+\.?\d*", f.readline())
        bitrate_str = matchobj[1]
        bitrate = float(bitrate_str)

        timecost = 0.0
        for row in f:
            if not row.startswith(" Total Time"):
                continue
            matchobj = re.search(r"(\d+\.?\d*) sec", row)
            timecost_str = matchobj.group(1)
            timecost = float(timecost_str)

        return EncodeLog(bitrate, timecost)

    @staticmethod
    def from_file(path: Path) -> EncodeLog:
        with path.open(encoding="utf-8") as f:
            return EncodeLog.load(f)
