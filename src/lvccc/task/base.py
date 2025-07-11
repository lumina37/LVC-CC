from __future__ import annotations

import abc
import dataclasses as dcs
import functools
import hashlib
from typing import TYPE_CHECKING, ClassVar

from ..config import get_config
from ..helper import to_json
from .factory import get_task_type

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from .abc import ProtoTask


@dcs.dataclass
class BaseTask[TSelfTask]:
    task: ClassVar[str] = ""

    children: list[ProtoTask] = dcs.field(default_factory=list, init=False, repr=False)
    chain: list[dict] = dcs.field(default_factory=list, init=False, repr=False)

    @property
    def parent(self) -> None:
        return None

    def ancestor(self, idx: int = -1) -> None:
        return None

    def fields(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict:
        fields = {"task": self.task}
        for field in dcs.fields(self):
            if exclude_if(field):
                continue
            val = getattr(self, field.name)
            fields[field.name] = val
        return fields

    def to_dicts(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> list[dict]:
        fields = self.fields(exclude_if)
        chain = self.chain.copy()
        chain.append(fields)
        return chain

    @staticmethod
    def from_dicts(chain: list[dict]) -> ProtoTask:
        fields = chain[-1]
        task_type = get_task_type(fields["task"])

        kwargs = {}
        for field in dcs.fields(task_type):
            if not field.init:
                continue
            if (val := fields.get(field.name, None)) is None:
                continue
            kwargs[field.name] = val

        self = task_type(**kwargs)
        self.chain = chain[:-1]  # Copy for safety

        return self

    def to_json(self, pretty: bool = False) -> str:
        json = to_json(self.to_dicts(), pretty=pretty)
        return json

    @functools.cached_property
    def hash(self) -> str:
        hashbytes = self.to_json().encode("utf-8")
        hashstr = hashlib.sha1(hashbytes, usedforsecurity=False).hexdigest()
        return hashstr

    @property
    def shorthash(self) -> str:
        return self.hash[:4]

    @property
    def self_tag(self) -> str:
        return ""

    @functools.cached_property
    def tag(self) -> str:
        return self.self_tag

    @functools.cached_property
    def dstdir(self) -> Path:
        config = get_config()
        real_dirname = f"{self.task}-{self.tag}-{self.shorthash}"
        return config.dir.output / "tasks" / real_dirname

    def dump_taskinfo(self, target: Path) -> None:
        with target.open("w", encoding="utf-8") as f:
            taskinfo = self.to_json(pretty=True)
            f.write(taskinfo)

    @abc.abstractmethod
    def run(self) -> None: ...


class RootTask[TSelfTask](BaseTask[TSelfTask]):
    pass


class NonRootTask[TSelfTask](BaseTask[TSelfTask]):
    @functools.cached_property
    def parent(self) -> ProtoTask:
        return self.ancestor()

    def ancestor(self, idx: int = -1) -> ProtoTask:
        end = idx + 1
        if end == 0:
            return BaseTask.from_dicts(self.chain)
        else:
            return BaseTask.from_dicts(self.chain[:end])

    @functools.cached_property
    def tag(self) -> str:
        parent_part = self.parent.tag
        prefix = "-" if self.self_tag else ""
        self_part = prefix + self.self_tag
        tag = parent_part + self_part
        return tag

    @functools.cached_property
    def seq_name(self) -> str:
        return self.chain[0]["seq_name"]

    @functools.cached_property
    def frames(self) -> int:
        return self.chain[0]["frames"]

    def follow(self, parent: ProtoTask) -> TSelfTask:
        # Appending `parent.fields()` to chain
        chain = parent.chain[:]
        chain.append(parent.fields())
        self.chain = chain

        # Appending reverse hooks to `parent`
        parent.children.append(self)

        return self
