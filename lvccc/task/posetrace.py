import dataclasses as dcs
import functools
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

import tomllib
from PIL import Image

from ..helper import mkdir, size_from_filename
from .base import NonRootTask, TVarTask
from .convert import ConvertTask
from .infomap import query


def is_rotated(seq_name: str) -> bool:
    rotated = False

    cfg_srcdir = Path("config") / seq_name
    with (cfg_srcdir / "calib.toml").open('rb') as f:
        table = tomllib.load(f)
        rotated = table["transpose"]

    return rotated


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

    rowidx = 0
    for row in range(views):
        colidx = rowidx + row * row_step
        for col in range(views):
            idx = colidx + col * col_step
            yield idx


def padding_comp(comp: bytes, in_size: tuple[int, int], out_size: tuple[int, int]) -> bytes:
    comp_img = Image.frombuffer('L', in_size, comp)

    width_resize = out_size[0] / in_size[0]
    height_resize = out_size[1] / in_size[1]
    resize_factor = min(width_resize, height_resize)
    if resize_factor < 1.0:
        target_width = round(in_size[0] * resize_factor)
        target_height = round(in_size[1] * resize_factor)
        comp_img = comp_img.resize((target_width, target_height), Image.Resampling.BOX)

    canvas = Image.new('L', out_size, 127)
    paste_left = (out_size[0] - comp_img.width) // 2
    paste_top = (out_size[1] - comp_img.height) // 2
    canvas.paste(comp_img, (paste_left, paste_top))

    canvas_bytes = canvas.tobytes()
    return canvas_bytes


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
        is_rot = is_rotated(self.seq_name)

        srcpaths = sorted((self.srcdir / 'yuv').glob('*.yuv'))
        width, height = size_from_filename(srcpaths[0].name)
        ysize = width * height
        uv_width = width // 2
        uv_height = height // 2
        uvsize = ysize // 4
        frame_size = ysize + uvsize * 2
        OUTSIZE = (1920, 1080)
        HALF_OUTSIZE = (OUTSIZE[0] // 2, OUTSIZE[1] // 2)

        mkdir(self.dstdir)
        dst_fname = f"{self.tag}-{OUTSIZE[0]}x{OUTSIZE[1]}.yuv"
        dstpath = self.dstdir / dst_fname

        with dstpath.open('wb') as dstf:
            frame_idx = 0
            eof = False
            while 1:
                for view_idx in view_indices(views, is_rot):
                    with srcpaths[view_idx].open('rb') as srcf:
                        srcf.seek(frame_idx * frame_size)
                        for _ in range(self.frame_per_view):
                            ycomp = srcf.read(ysize)
                            ucomp = srcf.read(uvsize)
                            vcomp = srcf.read(uvsize)

                            padded_ycomp = padding_comp(ycomp, (width, height), OUTSIZE)
                            dstf.write(padded_ycomp)
                            padded_ucomp = padding_comp(ucomp, (uv_width, uv_height), HALF_OUTSIZE)
                            dstf.write(padded_ucomp)
                            padded_vcomp = padding_comp(vcomp, (uv_width, uv_height), HALF_OUTSIZE)
                            dstf.write(padded_vcomp)

                            frame_idx += 1
                            if frame_idx == self.frames:
                                eof = True
                                break

                    if eof:
                        break

                if eof:
                    break
