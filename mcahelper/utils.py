import json
import re
import subprocess
import traceback
from pathlib import Path

from .logging import get_logger


def to_json(dic: dict, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(dic, indent=4)
    else:
        return json.dumps(dic, separators=(',', ':'))


def mkdir(path: Path):
    path = Path(path)
    path.mkdir(0o755, parents=True, exist_ok=True)


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


def get_first_file(d: Path, glob_pattern: str = '*.png') -> Path:
    return next(d.glob(glob_pattern))


def get_src_pattern(sample: str) -> str:
    number = re.search(r'(\d+)\.png', sample).group(1)  # match '001' in 'frame_001.png'
    pattern = re.sub(r'(\d+)(?=\.png)', f'%0{len(number)}d', sample)  # turn into 'frame_%03d.png'
    number = int(number)
    return pattern, number


def get_src_startidx(sample: str) -> int:
    number = re.search(r'(\d+)\.png', sample).group(1)  # match '001' in 'frame_001.png'
    number = int(number)
    return number


def get_QP(name: str) -> int:
    qp = int(name.removeprefix("QP#"))
    return qp
