import tempfile
from pathlib import Path

import numpy as np

from ..config import get_node_cfg
from .command import run_cmds
from .readlog import read_psnrlog


def compute_psnr_yuv(lhs: Path, rhs: Path, width: int, height: int) -> np.ndarray:
    with tempfile.NamedTemporaryFile('w', delete_on_close=False) as tf:
        tf.close()

        node_cfg = get_node_cfg()
        temp_path = Path(tf.name)
        temp_path_str = str(temp_path).replace('\\', '/').replace(':', '\\:')
        cmds = [
            node_cfg.app.ffmpeg,
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "yuv420p",
            "-i",
            lhs,
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "yuv420p",
            "-i",
            rhs,
            "-lavfi",
            f"psnr=stats_file='{temp_path_str}'",
            "-v",
            "warning",
            "-f",
            "null",
            "-",
        ]
        run_cmds(cmds)

        psnr = read_psnrlog(temp_path)

    psnrarr = np.asarray([psnr.y, psnr.u, psnr.v])
    return psnrarr
