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
    def getval_from_meta(meta: dict, key: str):
        mca_meta = meta.get(DataclsCfg.KEY, {})
        mca_cfg = DataclsCfg(**mca_meta)
        val = getattr(mca_cfg, key)
        return val
