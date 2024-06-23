from . import factory, infomap, iterator
from .base import BaseTask
from .codec import CodecTask
from .copy import CopyTask
from .png2yuv import Png2yuvTask
from .postproc import PostprocTask
from .preproc import PreprocTask
from .rlc import RLCRenderTask
from .yuv2png import Yuv2pngTask

factory.register(CodecTask)
factory.register(CopyTask)
factory.register(Png2yuvTask)
factory.register(PostprocTask)
factory.register(PreprocTask)
factory.register(RLCRenderTask)
factory.register(Yuv2pngTask)
