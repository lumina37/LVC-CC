import json


def to_json(dic: dict, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(dic, indent=4)
    else:
        return json.dumps(dic, separators=(",", ":"))
