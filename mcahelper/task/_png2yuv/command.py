from ...cfg.node import get_node_cfg


def build(frames: int, src: str, dst: str) -> list[str]:
    node_cfg = get_node_cfg()

    frames = str(frames)
    src = str(src)
    dst = str(dst)

    return [
        node_cfg.app.ffmpeg,
        "-i",
        src,
        "-vf",
        "format=yuv420p",
        "-vframes",
        frames,
        dst,
        "-v",
        "warning",
        "-y",
    ]
