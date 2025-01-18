from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..config import get_config
from ..task import Chain, ProtoTask

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


def tasks(
    cls: type[ProtoTask] | None = None, require: Callable[[ProtoTask], bool] | None = lambda _: True
) -> Generator[ProtoTask]:
    config = get_config()

    tasks_dir = config.dir.output / "tasks"
    glob_pattern = f"{cls.task}*" if cls is not None else "*"
    for d in tasks_dir.glob(glob_pattern):
        if not d.is_dir():
            continue

        taskinfo_path = d / "task.json"
        if not taskinfo_path.exists():
            continue

        with taskinfo_path.open(encoding="utf-8") as f:
            taskinfo = json.load(f)
            chain = Chain(taskinfo)
            task = chain[-1]
            if not require(task):
                continue
            yield task
