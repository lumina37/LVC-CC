from . import factory
from .abc import ProtoChain, ProtoTask
from .base import NonRootTask, RootTask
from .chain import Chain
from .codec import CodecTask, VtmType
from .convert import ConvertTask
from .convert40 import Convert40Task
from .copy import CopyTask
from .infomap import gen_infomap, get_infomap, query
from .posetrace import PosetraceTask
from .postproc import PostprocTask
from .preproc import PreprocTask

factory.reg_task_type(CodecTask)
factory.reg_task_type(CopyTask)
factory.reg_task_type(PostprocTask)
factory.reg_task_type(PreprocTask)
factory.reg_task_type(ConvertTask)
factory.reg_task_type(Convert40Task)
factory.reg_task_type(PosetraceTask)
