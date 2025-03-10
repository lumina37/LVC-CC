import sys

from lvccc.config import update_config
from lvccc.task import query
from lvccc.utils import tasks

config_fname = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
config = update_config(config_fname)

for task in tasks():
    curr_path = query(task)
    if curr_path != task.dstdir:
        curr_path.rename(task.dstdir)
        print(f"Renaming {curr_path.name} to {task.dstdir.name}")
