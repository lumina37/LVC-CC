from typing import List


def build(preprocess: str, cfg: str, src: str, dst: str) -> List[str]:
    preprocess = str(preprocess)
    cfg = str(cfg)
    src = str(src)
    dst = str(dst)

    return [
        preprocess,
        cfg,
        src,
        dst,
    ]
