from . import factory, iterator
from .base import BaseTask
from .codec import CodecTask
from .png2yuv import Png2yuvTask
from .postproc import PostprocTask
from .preproc import PreprocTask
from .render import RenderTask
from .yuv2png import Yuv2pngTask

factory.register(CodecTask)
factory.register(Png2yuvTask)
factory.register(PostprocTask)
factory.register(PreprocTask)
factory.register(RenderTask)
factory.register(Yuv2pngTask)
