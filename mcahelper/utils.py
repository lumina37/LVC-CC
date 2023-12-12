import re
import subprocess
from pathlib import Path


def mkdir(path: Path):
    path = Path(path)
    path.mkdir(0o755, parents=True, exist_ok=True)


def run_cmds(cmds: list):
    return subprocess.run([str(cmd) for cmd in cmds])


def get_first_file(d: Path, glob_pattern: str = '*.png') -> Path:
    return next(d.glob(glob_pattern))


def get_src_pattern(sample: str) -> str:
    number = re.search(r'(\d+)\.png', sample).group(1)  # match '001' in 'frame_001.png'
    pattern = re.sub(r'(\d+)(?=\.png)', f'%0{len(number)}d', sample)  # turn into 'frame_%03d.png'
    return pattern


def get_QP(name: str) -> int:
    qp = int(name.removeprefix("QP#"))
    return qp
