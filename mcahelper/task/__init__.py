from . import factory
from .codec import CodecTask
from .png2yuv import Png2yuvTask
from .preproc import PreprocTask
from .yuv2png import Yuv2pngTask

factory.register(CodecTask)
factory.register(Png2yuvTask)
factory.register(PreprocTask)
factory.register(Yuv2pngTask)
