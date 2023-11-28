from typing import List

from ..config import get_rootcfg


def build(width: int, height: int, src: str, dst: str) -> List[str]:
    rootcfg = get_rootcfg()

    src = str(src)
    dst = str(dst)

    return [
        rootcfg['app']['ffmpeg'],
        "-s",
        f"{width}x{height}",
        "-i",
        src,
        "-vf",
        "format=yuv444p",
        dst,
        "-v",
        "warning",
    ]
