import dataclasses as dcs
from pathlib import Path
from typing import TextIO

from .base import AutoConvImpl


@dcs.dataclass
class PreprocCfg(AutoConvImpl):
    FramesToBeEncoded: int = 30
    SourceWidth: int = 1920
    SourceHeight: int = 1080

    def dump(self, f: TextIO) -> None:
        f.writelines(f"{k} : {v}\n" for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIO) -> "PreprocCfg":
        fields = {field.name for field in dcs.fields(PreprocCfg)}

        def _items():
            for row in f:
                key, value = row.replace("\t", " ").split(":", maxsplit=1)
                key = key.rstrip()
                value = value.lstrip().rstrip("\n")
                if key not in fields:
                    continue
                yield key, value

        return PreprocCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "PreprocCfg":
        with path.open(encoding="utf-8") as f:
            return PreprocCfg.load(f)
