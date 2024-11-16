from . import factory
from .abc import ProtoChain, ProtoTask, TRetTask, TSelfTask, TVarTask
from .base import NonRootTask, RootTask
from .chain import Chain
from .codec import CodecTask, VtmType
from .convert import ConvertTask
from .copy import ImgCopyTask, YuvCopyTask
from .img2yuv import Img2yuvTask
from .infomap import gen_infomap, get_infomap, query
from .posetrace import PosetraceTask
from .postproc import PostprocTask
from .preproc import PreprocTask
from .yuv2img import Yuv2imgTask

factory.reg_task_type(CodecTask)
factory.reg_task_type(ImgCopyTask)
factory.reg_task_type(YuvCopyTask)
factory.reg_task_type(Img2yuvTask)
factory.reg_task_type(PostprocTask)
factory.reg_task_type(PreprocTask)
factory.reg_task_type(ConvertTask)
factory.reg_task_type(Yuv2imgTask)
factory.reg_task_type(PosetraceTask)
