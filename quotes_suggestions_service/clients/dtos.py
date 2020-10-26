from dataclasses import dataclass
from typing import Optional

from quotes_suggestions_service.utils.helpers import return_only_lower_letters


@dataclass(frozen=True)
class Quote:

    quote: str
    author: str
    description: Optional[str] = None

    def __hash__(self):
        return hash(return_only_lower_letters(self.quote.lower() + self.author.lower()))

    def __eq__(self, other):
        if isinstance(other, Quote):
            return self.__hash__() == other.__hash__()

    def to_bytes(self):
        pass
