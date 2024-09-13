import json

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from lvccc.config import update_config
from lvccc.helper import mkdir
from lvccc.task import (
    CodecTask,
    ComposeTask,
    Img2yuvTask,
    PostprocTask,
    PreprocTask,
    RenderTask,
    Yuv2imgTask,
    YuvCopyTask,
    gen_infomap,
)

config = update_config('config.toml')

summary_dir = config.path.output / 'summary'
src_dir = summary_dir / 'tasks'
dst_dir = summary_dir / 'figure'
mkdir(dst_dir)

infomap = gen_infomap(src_dir)


for seq_name in config.cases.seqs:
    tcopy = YuvCopyTask(seq_name=seq_name, frames=config.frames)
    tyuv2img = Yuv2imgTask().with_parent(tcopy)
    tpreproc = PreprocTask().with_parent(tyuv2img)
    timg2yuv = Img2yuvTask().with_parent(tpreproc)

    for vtm_type in config.cases.vtm_types:
        bitrates = []
        psnrs = []

        for qp in config.QP.wMCA.get(seq_name, []):
            tcodec = CodecTask(vtm_type=vtm_type, qp=qp).with_parent(timg2yuv)
            tyuv2img = Yuv2imgTask().with_parent(tcodec)
            tpostproc = PostprocTask().with_parent(tyuv2img)
            trender = RenderTask().with_parent(tpostproc)
            tcompose = ComposeTask().with_parent(trender)

            json_path = src_dir / tcodec.full_tag / "psnr.json"
            if not json_path.exists():
                continue

            with json_path.open() as f:
                metrics: dict = json.load(f)

            bitrates.append(metrics['bitrate'])
            psnrs.append(metrics['mvpsnr_y'])

        fig, ax = plt.subplots(figsize=(6, 6))
        ax: Axes = ax
        ax.set_xlabel("Total bitrate (Kbps)")
        ax.set_ylabel("PSNR (dB)")
        title = f'{seq_name}'
        ax.set_title(title)

        ax.plot(bitrates, psnrs)

        label = 'anchor'
        fname = f"{label}-{seq_name}-{vtm_type}"
        fig.savefig((dst_dir / fname).with_suffix('.png'))
        fig.savefig((dst_dir / fname).with_suffix('.svg'))
