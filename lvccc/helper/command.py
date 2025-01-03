import subprocess
import traceback
from io import TextIOBase
from pathlib import Path

from ..logging import get_logger


def run_cmds(cmds: list, output: TextIOBase | None = None, cwd: Path | None = None):
    log = get_logger()

    try:
        strcmds = [str(cmd) for cmd in cmds]
        subprocess.run(strcmds, stdout=output, stderr=subprocess.STDOUT, text=True, cwd=cwd, check=True)

    except Exception:
        log.error(f"Failed! err={traceback.format_exc()}")
        raise

    else:
        log.info(f"Completed! cmds={strcmds}")
