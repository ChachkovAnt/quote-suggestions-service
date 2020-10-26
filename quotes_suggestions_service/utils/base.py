from typing import Iterable
from enum import Enum


class StringEnum(Enum):

    def values(self) -> Iterable[str]:
        return tuple(self.__dict__.values())
