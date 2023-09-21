from pathlib import Path

from helper.configs.self import Cfg
from vvc_dec2png import dec2png

cfg = Cfg.from_file(Path('pipeline_ref.toml'))

if __name__ == "__main__":
    cfg = Cfg.from_file(Path('pipeline.toml'))
    dec2png(cfg)
