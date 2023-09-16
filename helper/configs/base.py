import dataclasses


class CfgBase(object):
    def __post_init__(self) -> None:
        for field in dataclasses.fields(self):
            raw_attr = self.__getattribute__(field.name)
            if isinstance(raw_attr, field.type):
                continue
            elif isinstance(raw_attr, dict):
                self.__setattr__(field.name, field.type(**raw_attr))
            else:
                self.__setattr__(field.name, field.type(raw_attr))
