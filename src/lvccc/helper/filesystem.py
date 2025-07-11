from __future__ import annotations

import shutil
from pathlib import Path


def mkdir(path: Path, mode: int = 0o755) -> None:
    path = Path(path)
    path.mkdir(mode, parents=True, exist_ok=True)


def remove(path: Path) -> None:
    path = Path(path)
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


def mtime(path: Path) -> int:
    return path.stat().st_mtime_ns


def get_first_file(d: Path, glob_pattern: str = "*") -> Path:
    return sorted(d.glob(glob_pattern))[0]


def get_any_file(d: Path, glob_pattern: str = "*") -> Path:
    return next(d.glob(glob_pattern))
