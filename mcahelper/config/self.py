from io import BufferedIOBase
from pathlib import Path

import tomllib

_ROOTCFG = None


def load(f: BufferedIOBase) -> dict:
    return tomllib.load(f)


def from_file(path: Path) -> dict:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)


def set_rootcfg(path: Path) -> dict:
    global _ROOTCFG
    _ROOTCFG = from_file(path)
    return _ROOTCFG


def get_rootcfg() -> dict:
    return _ROOTCFG
