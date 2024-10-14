import dataclasses as dcs
from typing import get_origin


@dcs.dataclass
class AdapterImpl:
    def __post_init__(self):
        for field in dcs.fields(self):
            value = getattr(self, field.name)

            ori_type = get_origin(field.type)
            if ori_type is None:
                ori_type = field.type

            if not isinstance(value, ori_type):
                value = getattr(self, field.name)
                if isinstance(value, dict):
                    setattr(self, field.name, field.type(**value))
                else:
                    setattr(self, field.name, field.type(value))


@dcs.dataclass
class UpdateImpl(AdapterImpl):
    def update(self, rhs: "UpdateImpl") -> "UpdateImpl":
        for field in dcs.fields(rhs):
            rhs_value = getattr(rhs, field.name)
            if not rhs_value:
                continue
            if hasattr(rhs_value, 'update'):
                lhs_value = getattr(self, field.name)
                lhs_value.update(rhs_value)
            else:
                setattr(self, field.name, rhs_value)
