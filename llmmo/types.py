from typing import Protocol, Union


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


type Jsonable = Union[
    None, int, bool, str, SupportsStr, list[Jsonable], dict[str, Jsonable]
]
