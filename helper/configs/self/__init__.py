import dataclasses
from io import BufferedIOBase
from pathlib import Path

import tomllib

from ..base import CfgBase
from .baseline_render import BaselineRenderCfg
from .codec import CodecCfg
from .computation import ComputationCfg
from .dec2png import Dec2PNGCfg
from .postprocess import PostprocessCfg
from .pre2yuv import Pre2YUVCfg
from .preprocess import PreprocessCfg
from .raw2png import Raw2PNGCfg
from .render import RenderCfg


@dataclasses.dataclass
class Cfg(CfgBase):
    dataset_root: Path = dataclasses.field(default_factory=Path)
    ffmpeg: Path = dataclasses.field(default_factory=Path)
    raw2png: Raw2PNGCfg = dataclasses.field(default_factory=Raw2PNGCfg)
    preprocess: PreprocessCfg = dataclasses.field(default_factory=PreprocessCfg)
    pre2yuv: Pre2YUVCfg = dataclasses.field(default_factory=Pre2YUVCfg)
    codec: CodecCfg = dataclasses.field(default_factory=CodecCfg)
    dec2png: Dec2PNGCfg = dataclasses.field(default_factory=Dec2PNGCfg)
    postprocess: PostprocessCfg = dataclasses.field(default_factory=PostprocessCfg)
    render: RenderCfg = dataclasses.field(default_factory=RenderCfg)
    baseline_render: BaselineRenderCfg = dataclasses.field(default_factory=BaselineRenderCfg)
    computation: ComputationCfg = dataclasses.field(default_factory=ComputationCfg)

    @staticmethod
    def load(f: BufferedIOBase) -> "Cfg":
        return Cfg(**tomllib.load(f))

    @staticmethod
    def from_file(path: Path) -> "Cfg":
        with path.open('rb') as f:
            return Cfg.load(f)
