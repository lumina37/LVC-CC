from __future__ import annotations

import dataclasses as dcs
import functools
from pathlib import Path
from typing import ClassVar

from .base import NonRootTask
from .convert import ConvertTask


@dcs.dataclass
class ConvertRefTask(ConvertTask, NonRootTask["ConvertRefTask"]):
    """
    Multi-view conversion.
    """

    task: ClassVar[str] = "convertref"

    @functools.cached_property
    def extra_args(self) -> list[str]:
        extra_args_path = Path("config") / self.seq_name / "ref" / "convert.sh"
        with extra_args_path.open() as f:
            extra_args = f.read().split(" ")
            return extra_args
