from typing import List


def build(postprocess: str, cfg: str, src: str, dst: str) -> List[str]:
    postprocess = str(postprocess)
    cfg = str(cfg)
    src = str(src)
    dst = str(dst)

    return [
        postprocess,
        cfg,
        src,
        dst,
    ]
