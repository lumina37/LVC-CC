import dataclasses as dcs
import functools
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

import numpy as np
import yuvio
from PIL import Image

from ..config import CalibCfg
from ..helper import size_from_filename
from .base import NonRootTask, TVarTask
from .convert import ConvertTask
from .infomap import query


def get_direction(seq_name: str) -> bool:
    direction = False

    cfg_srcdir = Path("config") / seq_name
    with (cfg_srcdir / "calib.cfg").open(encoding="utf-8") as f:
        calib_cfg = CalibCfg.load(f)
        direction = calib_cfg.MLADirection

    return direction


def get_views(task: TVarTask) -> int:
    views = 5

    for t in task.chain:
        if isinstance(t, ConvertTask):
            views = t.views
            break

    return views


def view_indices(views: int, is_rot: bool) -> Iterator[int]:
    if is_rot:
        row_step, col_step = 1, views
    else:
        row_step, col_step = views, 1

    forward = True
    row_idx = 0
    for row in range(views):
        row_idx = row * row_step
        if not forward:
            row_idx += (views - 1) * col_step
        for col in range(views):
            idx = row_idx + col * (col_step if forward else -col_step)
            yield idx
        forward = not forward


def padding_img(img: Image.Image, out_size: tuple[int, int]) -> Image:
    width_resize = out_size[0] / img.width
    height_resize = out_size[1] / img.height
    resize_factor = min(width_resize, height_resize)
    if resize_factor < 1.0:
        target_width = round(img.width * resize_factor)
        target_height = round(img.height * resize_factor)
        img = img.resize((target_width, target_height), Image.Resampling.BOX)

    canvas = Image.new("L", out_size, 0)  # TODO: should be 127
    paste_left = (out_size[0] - img.width) // 2
    paste_top = (out_size[1] - img.height) // 2
    canvas.paste(img, (paste_left, paste_top))

    return canvas


def padding(src: yuvio.core.YUVFrame, out_size: tuple[int, int]) -> bytes:
    uv_out_size = (out_size[0] // 2, out_size[1] // 2)

    ysrc = Image.fromarray(src.y)
    ydst = padding_img(ysrc, out_size)
    usrc = Image.fromarray(src.u)
    udst = padding_img(usrc, uv_out_size)
    vsrc = Image.fromarray(src.v)
    vdst = padding_img(vsrc, uv_out_size)

    dst_frame = yuvio.frame((np.asarray(ydst), np.asarray(udst), np.asarray(vdst)), "yuv420p")

    return dst_frame


@dcs.dataclass
class PosetraceTask(NonRootTask["PosetraceTask"]):
    task: ClassVar[str] = "posetrace"

    frame_per_view: int = 1

    @functools.cached_property
    def srcdir(self) -> Path:
        srcdir = query(self.parent)
        return srcdir

    def _inner_run(self) -> None:
        views = get_views(self)
        is_rot = get_direction(self.seq_name)

        src_paths = sorted((self.srcdir / "yuv").glob("*.yuv"))
        src_wdt, src_hgt = size_from_filename(src_paths[0].name)

        dst_wdt, dst_hgt = 1920, 1080
        dst_fname = f"{self.tag}-{dst_wdt}x{dst_hgt}.yuv"
        writer = yuvio.get_writer(self.dstdir / dst_fname, dst_wdt, dst_hgt, "yuv420p")

        frame_idx = 0
        eof = False
        while 1:
            for view_idx in view_indices(views, is_rot):
                reader = yuvio.get_reader(src_paths[view_idx], src_wdt, src_hgt, "yuv420p")
                for _ in range(self.frame_per_view):
                    src = reader.read(frame_idx, 1)[0]
                    dst = padding(src, (dst_wdt, dst_hgt))
                    writer.write(dst)

                    frame_idx += 1
                    if frame_idx == self.frames:
                        eof = True
                        break

                if eof:
                    break

            if eof:
                break
