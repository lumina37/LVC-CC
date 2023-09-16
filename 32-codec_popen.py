import asyncio
import subprocess
from pathlib import Path

import cv2 as cv

from helper.configs.self import Cfg
from helper.configs.vtm import VTMCfg

cfg = Cfg.from_file(Path('pipeline_ref.toml'))
codec_cfg = cfg.codec

process_num = 10
task_queue: asyncio.Queue[subprocess.Popen] = asyncio.Queue(process_num - 2)


async def task_launcher():
    for dataset_dir in cfg.dataset_root.iterdir():
        ref_img = cv.imread(str(dataset_dir / codec_cfg.size_ref_img_file))
        height, width = ref_img.shape[:2]

        vtm_cfg = VTMCfg.from_file(dataset_dir / codec_cfg.param_file)
        vtm_cfg.SourceHeight = height
        vtm_cfg.SourceWidth = width
        vtm_cfg.to_file(dataset_dir / codec_cfg.temp_param_file)

        for iqp in range(4):
            qp_start = 31
            qp_step = 5
            qp = qp_start + iqp * qp_step

            def fmt_and_mkdir(fp_fstr: str) -> str:
                fp_str = fp_fstr.format(qp=qp)
                fp = dataset_dir / fp_str
                fp.parent.mkdir(0o755, parents=True, exist_ok=True)
                return str(fp)

            dst_file_str = fmt_and_mkdir(codec_cfg.dst_file_fstr)
            log_file_str = fmt_and_mkdir(codec_cfg.log_file_fstr)
            recon_file_str = fmt_and_mkdir(codec_cfg.recon_file_fstr)

            with (dataset_dir / log_file_str).open('w') as out:
                process = subprocess.Popen(
                    [
                        str(codec_cfg.program),
                        "-c",
                        str(codec_cfg.encode_mode_cfg_file),
                        "-c",
                        str(dataset_dir / codec_cfg.temp_param_file),
                        "-i",
                        str(dataset_dir / codec_cfg.src_file),
                        "-b",
                        dst_file_str,
                        "-o",
                        recon_file_str,
                        "--InternalBitDepth=8",
                        f"--QP={qp}",
                        "--FramesToBeEncoded=1",
                    ],
                    stdout=out,
                    text=True,
                )
                print(f"Launched: name={dataset_dir.name} qp={qp}")
                await task_queue.put(process)


async def waiter():
    while 1:
        try:
            process = await asyncio.wait_for(task_queue.get(), timeout=2.0)
        except asyncio.TimeoutError:
            return
        else:
            process.wait()


async def main():
    await asyncio.gather(task_launcher(), waiter())


asyncio.run(main())
