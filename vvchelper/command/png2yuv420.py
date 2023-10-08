from typing import List


def build(ffmpeg: str, frames: int, src: str, dst: str) -> List[str]:
    ffmpeg = str(ffmpeg)
    frames = int(frames)
    src = str(src)
    dst = str(dst)

    return [
        ffmpeg,
        "-i",
        src,
        "-vf",
        "format=yuv420p",
        "-vframes",
        str(frames),
        dst,
        "-v",
        "warning",
        "-y",
    ]
