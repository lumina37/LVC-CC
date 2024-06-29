from . import factory
from .base import TDerivedTask
from .codec import CodecTask
from .compose import ComposeTask
from .copy import CopyTask
from .iterator import get_codec_task, tasks
from .png2yuv import Png2yuvTask
from .postproc import PostprocTask
from .preproc import PreprocTask
from .render import RenderTask
from .yuv2png import Yuv2pngTask

factory.register(CodecTask)
factory.register(ComposeTask)
factory.register(CopyTask)
factory.register(Png2yuvTask)
factory.register(PostprocTask)
factory.register(PreprocTask)
factory.register(RenderTask)
factory.register(Yuv2pngTask)
