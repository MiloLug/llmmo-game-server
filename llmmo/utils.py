import orjson

from llmmo.types import Jsonable


def _json_arbitrary_serializer(obj):
    if type(obj).__str__ is not object.__str__:
        # We need only the custom __str__ method,
        # to not accidentally serialize objects that are not meant to be serialized.
        return str(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def json_dumps(data: Jsonable, indent=False) -> str:
    flags = orjson.OPT_SERIALIZE_UUID | orjson.OPT_OMIT_MICROSECONDS
    if indent:
        flags |= orjson.OPT_INDENT_2

    return orjson.dumps(data, option=flags, default=_json_arbitrary_serializer).decode()


def json_loads(data: str) -> Jsonable:
    return orjson.loads(data)
