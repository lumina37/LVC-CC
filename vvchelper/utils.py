import re
from pathlib import Path


def mkdir(path: Path):
    path = Path(path)
    path.mkdir(0o755, parents=True, exist_ok=True)


def path_from_root(rootcfg: dict, path: Path):
    if not isinstance(path, Path):
        path = Path(path)

    assert not path.is_absolute()

    abs_path = Path(rootcfg['root']) / path
    return abs_path


def get_src_pattern(sample: str) -> str:
    number = re.search(r'(\d+)\.png', sample).group(1)  # match '001' in 'frame_001.png'
    pattern = re.sub(r'(\d+)(?=\.png)', f'%0{len(number)}d', sample)  # turn into 'frame_%03d.png'
    return pattern


def get_QP(name: str) -> int:
    qp = int(name.removeprefix("QP#"))
    return qp
