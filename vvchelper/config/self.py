from io import BufferedIOBase
from pathlib import Path

import tomllib


def load(f: BufferedIOBase) -> dict:
    return tomllib.load(f)


def from_file(path: Path) -> dict:
    path = Path(path)
    with path.open('rb') as f:
        return load(f)
