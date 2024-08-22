import dataclasses as dcs
from pathlib import Path
from typing import ClassVar, TextIO

from pydantic.dataclasses import dataclass


@dataclass
class TLCTCfg:
    CFG_NAME: ClassVar[str] = "TLCT"

    pipeline: int = 1
    viewNum: int = 5
    rmode: int = 1
    Calibration_xml: str = ""
    RawImage_Path: str = ""
    Output_Path: str = ""
    start_frame: int = 1
    end_frame: int = 1
    height: int = 2048
    width: int = 2048
    upsample: int = 1
    patternSize: float = 0.325
    gradientBlendingWidth: float = 0.225
    psizeShortcutThreshold: float = -0.9

    def dump(self, f: TextIO) -> None:
        maxlen = 0
        for field in dcs.fields(self):
            if (flen := len(field.name)) > maxlen:
                maxlen = flen

        fstr = f"{{k:<{maxlen+2}}}{{v}}\n"
        f.writelines(fstr.format(k=k, v=v) for k, v in dcs.asdict(self).items())
        f.flush()

    @staticmethod
    def load(f: TextIO) -> "TLCTCfg":
        def _items():
            for row in f:
                key, value = row.replace('\t', ' ').split(' ', maxsplit=1)
                value = value.lstrip().rstrip('\n')
                yield key, value

        return TLCTCfg(**dict(_items()))

    def to_file(self, path: Path) -> None:
        with path.open('w') as f:
            self.dump(f)

    @staticmethod
    def from_file(path: Path) -> "TLCTCfg":
        with path.open(encoding='utf-8') as f:
            return TLCTCfg.load(f)
