from typing import List

from ..config import get_rootcfg


def build(cfg: str) -> List[str]:
    rootcfg = get_rootcfg()

    cfg = str(cfg)

    return [
        rootcfg['app']['rlc'],
        cfg,
    ]
