from typing import List


def build(ffmpeg: str, frames: int, width: int, height: int, src: str, dst: str) -> List[str]:
    ffmpeg = str(ffmpeg)
    frames = int(frames)
    src = str(src)
    dst = str(dst)

    return [
        ffmpeg,
        "-s",
        f"{width}x{height}",
        "-frames",
        str(frames),
        "-i",
        src,
        "-vf",
        "format=yuv444p",
        dst,
        "-v",
        "warning",
    ]
