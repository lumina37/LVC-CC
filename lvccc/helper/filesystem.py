import shutil
from pathlib import Path


def mkdir(path: Path):
    path = Path(path)
    path.mkdir(0o755, parents=True, exist_ok=True)


def rm(path: Path):
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


def get_first_file(d: Path, glob_pattern: str = '*') -> Path:
    return next(d.glob(glob_pattern))
