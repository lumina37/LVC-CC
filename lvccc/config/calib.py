import dataclasses as dcs
from pathlib import Path
from typing import TextIO

from .base import AutoConvImpl


@dcs.dataclass
class CalibCfg(AutoConvImpl):
    pipeline: int = 0
    height: int = 2048
    width: int = 2048
    transpose: bool = False

    def dump(self, f: TextIO) -> None:
        maxlen = 0
        for field in dcs.fields(self):
            if (flen := len(field.name)) > maxlen:
                maxlen = flen

        fstr = f"{{k:<{maxlen}}}: {{v}}\n"
        f.writelines(fstr.format(k=k, v=v) for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIO) -> "CalibCfg":
        fields = {field.name for field in dcs.fields(CalibCfg)}

        def _items():
            for row in f:
                key, value = row.replace('\t', ' ').split(':', maxsplit=1)
                key = key.rstrip()
                value = value.lstrip().rstrip('\n')
                if key not in fields:
                    continue
                yield key, value

        return CalibCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w', encoding='utf-8') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "CalibCfg":
        with path.open(encoding='utf-8') as f:
            return CalibCfg.load(f)
