from typing import List

from ..config import get_rootcfg


def build(cfg: str, src: str, dst: str) -> List[str]:
    rootcfg = get_rootcfg()

    cfg = str(cfg)
    src = str(src)
    dst = str(dst)

    return [
        rootcfg['app']['preproc'],
        cfg,
        src,
        dst,
    ]
