from typing import List

from ..config import get_rootcfg


def build(mode_cfg: str, cfg: str, qp: int, src: str, encoded: str, decoded: str) -> List[str]:
    rootcfg = get_rootcfg()

    mode_cfg = str(mode_cfg)
    cfg = str(cfg)
    src = str(src)
    encoded = str(encoded)
    decoded = str(decoded)

    return [
        rootcfg['app']['encoder'],
        "-c",
        mode_cfg,
        "-c",
        cfg,
        "--InternalBitDepth=10",
        "--OutputBitDepth=8",
        f"--FramesToBeEncoded={rootcfg['common']['frames']}",
        "--TemporalSubsampleRatio=1",
        f"--QP={qp}",
        "-i",
        src,
        "-b",
        encoded,
        "-o",
        decoded,
    ]
