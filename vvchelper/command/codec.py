from typing import List


def build(encoder: str, mode_cfg: str, cfg: str, qp: int, src: str, encoded: str, decoded: str) -> List[str]:
    encoder = str(encoder)
    mode_cfg = str(mode_cfg)
    cfg = str(cfg)
    src = str(src)
    encoded = str(encoded)
    decoded = str(decoded)

    return [
        encoder,
        "-c",
        mode_cfg,
        "-c",
        cfg,
        "--InteralBitDepth=10",
        "--OutputBitDepth=8",
        "--FramesToBeEncoded=30",
        "--TemporalSubsampleRatio=1",
        f"--QP={qp}",
        "-i",
        src,
        "-b",
        encoded,
        "-o",
        decoded,
    ]
