import re
from pathlib import Path

from .config.self import get_rootcfg


def get_root() -> Path:
    rootcfg = get_rootcfg()
    root = rootcfg['common']['root'].rstrip('/').rstrip('\\')
    root = Path(root)
    return root


def mkdir(path: Path):
    path = Path(path)
    path.mkdir(0o755, parents=True, exist_ok=True)


def get_src_pattern(sample: str) -> str:
    number = re.search(r'(\d+)\.png', sample).group(1)  # match '001' in 'frame_001.png'
    pattern = re.sub(r'(\d+)(?=\.png)', f'%0{len(number)}d', sample)  # turn into 'frame_%03d.png'
    return pattern


def get_QP(name: str) -> int:
    qp = int(name.removeprefix("QP#"))
    return qp
