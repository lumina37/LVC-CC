from __future__ import annotations

import abc
import dataclasses as dcs
import functools
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, TypeVar


class ProtoChain(Sequence):
    @property
    def objs(self) -> list[dict]: ...

    def __getitem__(self, idx) -> ProtoTask: ...

    def copy(self) -> ProtoChain: ...

    def to_json(self, pretty: bool = False) -> str: ...


TVarTask = TypeVar("TVarTask", bound="ProtoTask")
TRetTask = TypeVar("TRetTask", bound="ProtoTask")
TSelfTask = TypeVar("TSelfTask", bound="ProtoTask")


class ProtoTask(Protocol):
    @property
    def task(self) -> str: ...
    @property
    def children(self) -> list[TRetTask]: ...
    @property
    def chain(self) -> ProtoChain: ...

    @property
    def seq_name(self) -> str: ...

    @functools.cached_property
    def parent(self) -> TRetTask | None: ...

    def fields(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> dict: ...

    def serialize(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> list[dict]: ...

    @classmethod
    def deserialize(cls, objs: list[dict]) -> TSelfTask: ...

    @functools.cached_property
    def chain_with_self(self) -> ProtoChain: ...

    @functools.cached_property
    def hash(self) -> int: ...

    @property
    def shorthash(self) -> str: ...

    @functools.cached_property
    def tag(self) -> str: ...

    @functools.cached_property
    def full_tag(self) -> str: ...

    @functools.cached_property
    def dstdir(self) -> Path: ...

    def dump_taskinfo(self, target: Path | None = None) -> None: ...

    @abc.abstractmethod
    def _run(self) -> None: ...

    def run(self) -> None: ...
