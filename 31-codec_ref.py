import multiprocessing as mp
from pathlib import Path

from helper.configs.self import Cfg
from vvc_codec import iter_args, run

if __name__ == "__main__":
    cfg = Cfg.from_file(Path('pipeline_ref.toml'))
    with mp.Pool(processes=12) as pool:
        pool.starmap_async(run, iter_args(cfg))
        pool.close()
        pool.join()
