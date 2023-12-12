from ...cfg.node import get_node_cfg


def build(width: int, height: int, src: str, dst: str) -> list[str]:
    node_cfg = get_node_cfg()

    src = str(src)
    dst = str(dst)

    return [
        node_cfg.app.ffmpeg,
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
