import subprocess
import traceback
from pathlib import Path

from ..logging import get_logger


def run_cmds(cmds: list, stdout_fpath: Path | None = None, cwd: Path | None = None):
    log = get_logger()

    try:
        strcmds = [str(cmd) for cmd in cmds]
        if stdout_fpath:
            with stdout_fpath.open('w') as f:
                subprocess.run(strcmds, stdout=f, text=True, cwd=cwd, check=True)
        else:
            subprocess.run(strcmds, cwd=cwd, check=True)

    except Exception:
        log.error(f"Failed! err={traceback.format_exc()}")
        raise

    else:
        log.info(f"Completed! cmds={cmds}")
