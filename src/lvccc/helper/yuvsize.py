from __future__ import annotations


def size_from_filename(filename: str) -> tuple[int, int]:
    filename = filename.removesuffix(".yuv")
    _, yuvsize = filename.rsplit("-", maxsplit=1)
    width, height = yuvsize.split("x", maxsplit=1)

    width = int(width)
    height = int(height)

    return width, height
