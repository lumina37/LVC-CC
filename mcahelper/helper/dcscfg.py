import dataclasses as dcs
from typing import ClassVar

from pydantic.dataclasses import dataclass


@dataclass
class DataclsCfg:
    KEY: ClassVar[str] = 'mca'

    ex_if_empty: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {self.KEY: dcs.asdict(self)}
