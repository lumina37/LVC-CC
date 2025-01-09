from __future__ import annotations

import re
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


def get_first_file(d: Path, glob_pattern: str = "*") -> Path:
    return sorted(d.glob(glob_pattern))[0]


def get_any_file(d: Path, glob_pattern: str = "*") -> Path:
    return next(d.glob(glob_pattern))


def detect_pattern(name: str) -> tuple[str, int]:
    match = list(re.finditer(r"(\d+)", name))[-1]
    num_start = match.start(match.lastindex)
    num_end = match.end(match.lastindex)
    start_idx = int(name[num_start:num_end])
    num_len = num_end - num_start
    pattern = name[:num_start] + f"%0{num_len}d" + name[num_end:]
    return pattern, start_idx
