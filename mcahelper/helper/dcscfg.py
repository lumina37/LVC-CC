import dataclasses as dcs
import functools
from typing import ClassVar

from pydantic.dataclasses import dataclass


@dataclass
class DataclsCfg:
    KEY: ClassVar[str] = 'mca'

    no_meta: bool = False
    no_hash: bool = False

    @functools.cached_property
    def D(self) -> dict[str, bool]:
        return {self.KEY: dcs.asdict(self)}

    @staticmethod
    def from_meta(meta: dict):
        mca_meta = meta.get(DataclsCfg.KEY, {})
        cfg = DataclsCfg(**mca_meta)
        return cfg
