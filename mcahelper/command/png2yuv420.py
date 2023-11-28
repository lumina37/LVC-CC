from typing import List

from ..config.self import get_rootcfg


def build(src: str, dst: str) -> List[str]:
    rootcfg = get_rootcfg()

    src = str(src)
    dst = str(dst)

    return [
        rootcfg['app']['ffmpeg'],
        "-i",
        src,
        "-vf",
        "format=yuv420p",
        "-vframes",
        str(rootcfg['common']['frames']),
        dst,
        "-v",
        "warning",
        "-y",
    ]
