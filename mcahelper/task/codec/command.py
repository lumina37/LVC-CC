from ...cfg.node import get_node_cfg


def build(vtm_type_cfg: str, cfg: str, frames: int, qp: int, src: str, encoded: str, decoded: str) -> list[str]:
    node_cfg = get_node_cfg()

    vtm_type_cfg = str(vtm_type_cfg)
    cfg = str(cfg)
    src = str(src)
    encoded = str(encoded)
    decoded = str(decoded)

    return [
        node_cfg.app.encoder,
        "-c",
        vtm_type_cfg,
        "-c",
        cfg,
        "--InternalBitDepth=10",
        "--OutputBitDepth=8",
        f"--FramesToBeEncoded={frames}",
        "--TemporalSubsampleRatio=1",
        f"--QP={qp}",
        "-i",
        src,
        "-b",
        encoded,
        "-o",
        decoded,
    ]
