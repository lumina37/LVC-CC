from __future__ import annotations

import hashlib
from pathlib import Path

from .filesystem import mkdir


class SHA1Cache:
    cache_dir = Path(".lvccc_cache")

    def __init__(self):
        if not self.cache_dir.exists():
            mkdir(self.cache_dir)
            with (self.cache_dir / ".gitignore").open("w") as f:
                f.write("*")

    def __getitem__(self, hsh: str) -> int:
        hsh_path = self.cache_dir / hsh
        if not hsh_path.exists():
            return 0
        with hsh_path.open("r") as f:
            mtime_str = f.read()
            mtime = int(mtime_str)
            return mtime

    def __setitem__(self, hsh: str, mtime: int) -> None:
        with (self.cache_dir / hsh).open("w") as f:
            mtime_str = str(mtime)
            f.write(mtime_str)


def get_sha1(path: Path) -> str:
    with path.open("r") as f:
        sha1 = f.read()
        return sha1


def compute_sha1(path: Path) -> str:
    sha1_state = hashlib.sha1(usedforsecurity=False)
    with path.open("rb") as yuvf:
        while chunk := yuvf.read(4 * 1024):
            sha1_state.update(chunk)
    sha1_hex = sha1_state.hexdigest()
    return sha1_hex
