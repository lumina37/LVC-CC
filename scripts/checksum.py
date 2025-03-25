import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.helper import SHA1Cache, compute_sha1, get_any_file, get_sha1, mtime
from lvccc.logging import get_logger

parser = argparse.ArgumentParser(description="Check SHA1 for all input sequences")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

logger = get_logger()

for seq_name in config.seqs:
    srcdir = config.dir.input / seq_name

    try:
        srcpath = get_any_file(srcdir, "*.yuv")
    except Exception:
        logger.warning(f"no sequence in {srcdir}")
        continue

    cfg_srcdir = Path("config") / seq_name
    sha1_path = cfg_srcdir / "checksum.sha1"
    except_sha1 = get_sha1(sha1_path)
    sha1_cache = SHA1Cache()
    cached_mtime = sha1_cache[except_sha1]
    if (yuv_mtime := mtime(srcpath)) > cached_mtime:
        sha1 = compute_sha1(srcpath)
        if sha1 != except_sha1:
            DOWNLOAD_URL = "https://content.mpeg.expert/data/CfP/LVC/Sequences"
            logger.warning(f"sha1 checksum does not match for {srcpath}, try redownload from: {DOWNLOAD_URL}")
            continue
        else:
            sha1_cache[sha1] = yuv_mtime
    logger.info(f"sha1 checksum matches for {srcpath}")
