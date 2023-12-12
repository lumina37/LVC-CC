from . import factory
from .png2yuv import Png2yuvTask
from .preproc import PreprocTask

factory.register(Png2yuvTask)
factory.register(PreprocTask)
