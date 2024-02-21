import dataclasses as dcs
from collections.abc import Callable
from typing import Protocol

from pydantic.dataclasses import dataclass


@dataclass
class Marshalable(Protocol):

    @classmethod
    def unmarshal(cls, dic: dict): ...

    def marshal(self, exclude_if: Callable[[dcs.Field], bool]) -> dict: ...
