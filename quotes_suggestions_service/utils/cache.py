from datetime import timedelta
from dataclasses import asdict
from json import dumps, loads
from typing import Tuple, Optional

from redis import Redis

from quotes_suggestions_service.clients.dtos import Quote


class TemporaryQuotesStorage:

    def __init__(self, host: str, port: int, cache_ttl: int):
        self.storage = Redis(host=host, port=port)
        self.cache_ttl = cache_ttl  # in seconds

    def set_cache(self, key: int, values: Tuple[Quote, ...]) -> bool:

        values = dumps({num: asdict(value) for num, value in enumerate(values)})

        return self.storage.setex(
            name=key,
            time=timedelta(seconds=self.cache_ttl),
            value=values)

    def get_cache(
            self,
            key: int,
            limit: Optional[int] = None,
            offset: Optional[int] = None) -> Tuple[Quote, ...]:

        if self.key_in_cache(key):
            self.storage.expire(key, time=self.cache_ttl)  # extend key ttl after each call
            data_from_storage = dict(loads(self.storage.get(key)))

            if limit is not None and offset is not None \
                    and limit+offset <= len(data_from_storage):
                data_from_storage = tuple(
                    data_from_storage[str(index)]  # Redis returns keys as string
                    for index in range(offset, limit+offset)
                )
            else:
                data_from_storage = data_from_storage.values()

            quotes = tuple(
                Quote(**raw_quote)
                for raw_quote in data_from_storage
            )
        else:
            quotes = ()

        return quotes

    def key_in_cache(self, key: int) -> bool:
        return bool(self.storage.exists(key))

    def reset_cache(self):
        self.storage.flushdb()
