from __future__ import annotations

import functools
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    import dataclasses as dcs
    from pathlib import Path


class ProtoChain(Sequence):
    @property
    def objs(self) -> list[dict]: ...

    def __getitem__(self, idx) -> ProtoTask: ...

    def copy(self) -> ProtoChain: ...


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

    def to_dicts(self, exclude_if: Callable[[dcs.Field], bool] = lambda f: not f.init) -> list[dict]: ...

    @classmethod
    def from_dicts(cls, objs: list[dict]) -> TSelfTask: ...

    def to_json(self, pretty: bool = False) -> str: ...

    @functools.cached_property
    def hash(self) -> int: ...

    @property
    def shorthash(self) -> str: ...

    @functools.cached_property
    def self_tag(self) -> str: ...

    @functools.cached_property
    def tag(self) -> str: ...

    @functools.cached_property
    def dstdir(self) -> Path: ...

    def dump_taskinfo(self, target: Path | None = None) -> None: ...

    def run(self) -> None: ...
