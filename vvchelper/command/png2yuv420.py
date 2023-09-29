from typing import List


def build(ffmpeg: str, src: str, dst: str) -> List[str]:
    ffmpeg = str(ffmpeg)
    src = str(src)
    dst = str(dst)

    return [
        ffmpeg,
        "-i",
        src,
        "-vf",
        "format=yuv420p",
        dst,
        "-v",
        "warning",
        "-y",
    ]
