from . import factory
from .abc import ProtoTask
from .base import BaseTask, NonRootTask, RootTask
from .codec import CodecTask
from .convert import ConvertTask
from .convert40 import Convert40Task
from .copy import CopyTask
from .decode import DecodeTask
from .encode import EncodeTask
from .infomap import gen_infomap, get_infomap, query
from .posetrace import PosetraceTask
from .postproc import OptimizeType, PostprocTask
from .preproc import PreprocTask

factory.reg_task_type(CodecTask)
factory.reg_task_type(EncodeTask)
factory.reg_task_type(DecodeTask)
factory.reg_task_type(CopyTask)
factory.reg_task_type(PostprocTask)
factory.reg_task_type(PreprocTask)
factory.reg_task_type(ConvertTask)
factory.reg_task_type(Convert40Task)
factory.reg_task_type(PosetraceTask)
