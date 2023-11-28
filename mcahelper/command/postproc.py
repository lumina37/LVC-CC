from typing import List

from ..config.self import get_rootcfg


def build(cfg: str, src: str, dst: str) -> List[str]:
    rootcfg = get_rootcfg()

    cfg = str(cfg)
    src = str(src)
    dst = str(dst)

    return [
        rootcfg['app']['postproc'],
        cfg,
        src,
        dst,
    ]
