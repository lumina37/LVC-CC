from __future__ import annotations

import abc
import dataclasses as dcs
import functools
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, SupportsIndex, TypeVar


class ProtoChain(Sequence):
    @property
    def objs(self) -> list[dict]: ...

    def __getitem__(self, idx: SupportsIndex) -> ProtoTask: ...

    def copy(self) -> ProtoChain: ...

    @property
    def serialized_str(self) -> str: ...


TVarTask = TypeVar("TVarTask", bound="ProtoTask")
TRetTask = TypeVar("TRetTask", bound="ProtoTask")
TSelfTask = TypeVar("TSelfTask", bound="ProtoTask")


class ProtoTask(Protocol):
    @property
    def task(self) -> str: ...
    @property
    def seq_name(self) -> str: ...
    @property
    def children(self) -> list[TRetTask]: ...
    @property
    def chain(self) -> ProtoChain: ...

    @functools.cached_property
    def parent(self) -> TRetTask | None: ...

    @classmethod
    def deserialize(cls, fields: dict) -> TSelfTask: ...

    def serialize(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.repr) -> dict: ...

    @functools.cached_property
    def fields(self) -> dict: ...

    @functools.cached_property
    def chain_with_self(self) -> ProtoChain: ...

    @functools.cached_property
    def hash(self) -> int: ...

    @property
    def shorthash(self) -> str: ...

    @abc.abstractmethod
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
