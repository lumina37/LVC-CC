from __future__ import annotations

import subprocess
import traceback
from typing import TYPE_CHECKING

from ..logging import get_logger

if TYPE_CHECKING:
    from io import TextIOBase
    from pathlib import Path


def run_cmds(cmds: list, output: TextIOBase | None = None, cwd: Path | None = None):
    log = get_logger()

    try:
        strcmds = [str(cmd) for cmd in cmds]
        subprocess.run(strcmds, stdout=output, stderr=subprocess.STDOUT, cwd=cwd, text=True, check=True)

    except Exception:
        log.error(f"Failed! err={traceback.format_exc()}")
        raise

    else:
        log.info(f"Completed! cmd={' '.join(strcmds)}")
