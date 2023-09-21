import multiprocessing as mp
import subprocess
from pathlib import Path

from helper.configs.self import Cfg
from vvc_render import iter_args

if __name__ == "__main__":
    cfg = Cfg.from_file(Path('pipeline_ref.toml'))
    with mp.Pool(processes=2) as pool:
        pool.map_async(subprocess.run, iter_args(cfg))
        pool.close()
        pool.join()
