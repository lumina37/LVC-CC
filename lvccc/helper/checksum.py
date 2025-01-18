from __future__ import annotations

import hashlib
from pathlib import Path

from .filesystem import mkdir


class MD5Cache:
    cache_dir = Path(".lvccc_cache")

    def __init__(self):
        mkdir(self.cache_dir)

    def __getitem__(self, hsh: str) -> int:
        hsh_path = self.cache_dir / hsh
        if not hsh_path.exists():
            return 0
        with hsh_path.open("r", encoding="utf-8") as f:
            mtime_str = f.read()
            mtime = int(mtime_str)
            return mtime

    def __setitem__(self, hsh: str, mtime: int) -> None:
        with (self.cache_dir / hsh).open("w", encoding="utf-8") as f:
            mtime_str = str(mtime)
            f.write(mtime_str)


def get_md5(path: Path):
    with path.open("r", encoding="utf-8") as f:
        md5 = f.read()
        return md5


def compute_md5(path: Path) -> str:
    md5_state = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as yuvf:
        while chunk := yuvf.read(4 * 1024):
            md5_state.update(chunk)
    md5_hex = md5_state.hexdigest()
    return md5_hex
