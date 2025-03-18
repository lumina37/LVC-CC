import argparse
from pathlib import Path

from lvccc.config import update_config
from lvccc.logging import get_logger
from lvccc.task import query
from lvccc.utils import tasks

parser = argparse.ArgumentParser(description="Anchor: convert/codec+convert")

parser.add_argument("--configs", "-c", nargs="+", type=str, default="", help="list of config file path")
parser.add_argument(
    "--base", "-b", type=str, default="base.toml", help="base config, recommended for per-device settings"
)
opt = parser.parse_args()

config = update_config(Path(opt.base))
for cpath in opt.configs:
    config = update_config(Path(cpath))

logger = get_logger()

for task in tasks():
    curr_path = query(task)
    if curr_path != task.dstdir:
        curr_path.rename(task.dstdir)
        logger.info(f"Renaming {curr_path.name} to {task.dstdir.name}")
