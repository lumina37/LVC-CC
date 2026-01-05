from .abc import ProtoTask
from .base import BaseTask, NonRootTask, RootTask
from .category import is_convert_task, reg_convert_task_type
from .convert import ConvertTask
from .convert40 import Convert40Task
from .convert45 import Convert45Task
from .convert_dbg import ConvertDbgTask
from .copy import CopyTask
from .decode import DecodeTask
from .encode import EncodeTask
from .factory import get_task_type, reg_task_type
from .infomap import gen_infomap, get_infomap, query
from .posetrace import PosetraceTask
from .postproc import PostprocTask
from .preproc import PreprocTask

reg_task_type(EncodeTask)
reg_task_type(DecodeTask)
reg_task_type(CopyTask)
reg_task_type(PostprocTask)
reg_task_type(PreprocTask)
reg_task_type(ConvertTask)
reg_task_type(ConvertDbgTask)
reg_task_type(Convert40Task)
reg_task_type(Convert45Task)
reg_task_type(PosetraceTask)

reg_convert_task_type(ConvertTask)
reg_convert_task_type(ConvertDbgTask)
reg_convert_task_type(Convert40Task)
reg_convert_task_type(Convert45Task)
