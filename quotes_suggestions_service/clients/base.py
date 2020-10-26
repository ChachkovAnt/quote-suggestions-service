from typing import Iterable, Tuple

from .dtos import Quote


class QuotesApiClient:
    """
    Interface for api clients
    """
    def get_quotes(self, authors: Iterable[str], keywords: Iterable[str]) -> Tuple[Quote, ...]:
        raise NotImplemented()
