from typing import List


def build(ffmpeg: str, width: int, height: int, src: str, dst: str) -> List[str]:
    ffmpeg = str(ffmpeg)
    src = str(src)
    dst = str(dst)

    return [
        ffmpeg,
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
