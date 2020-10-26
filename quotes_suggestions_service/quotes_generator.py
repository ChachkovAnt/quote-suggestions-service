from typing import Tuple, Set

from nltk import word_tokenize
from nltk.corpus import stopwords

from quotes_suggestions_service.setting import DEFAULT_CACHE_TTL, REDIS_HOST, REDIS_PORT
from quotes_suggestions_service.clients import EN_QUOTES_API_CLIENTS
from quotes_suggestions_service.clients.dtos import Quote
from quotes_suggestions_service.utils.cache import TemporaryQuotesStorage
from quotes_suggestions_service.utils.helpers import return_only_lower_letters


class QuotesGenerator:

    _instance = None
    cache_storage = TemporaryQuotesStorage(REDIS_HOST, REDIS_PORT, DEFAULT_CACHE_TTL)
    quotes_clients = EN_QUOTES_API_CLIENTS
    stop_words = set(stopwords.words("english"))

    def get_quotes(
            self,
            authors: Tuple[str],
            keywords: Tuple[str],
            limit: int = 1,
            offset: int = 0) -> Tuple[Quote, ...]:

        key = self._generate_key_from_string(''.join((*authors, *keywords)))

        if self.cache_storage.key_in_cache(key):
            response = self.cache_storage.get_cache(key, limit, offset)
        else:
            quotes_set = {
                quote
                for client in self.quotes_clients
                for quote in client.get_quotes(
                    authors=authors if len(authors) != 0 else (),
                    keywords=keywords if len(keywords) != 0 else ())
            }
            sorted_quotes = self._sort_quotes_by_matching(keywords, quotes_set)
            self.cache_storage.set_cache(key, sorted_quotes)
            response = sorted_quotes[offset:limit+offset]

        return response

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QuotesGenerator, cls).__new__(cls)

        return cls._instance

    def _sort_quotes_by_matching(
            self, keywords: Tuple[str], quotes_set: Set[Quote]) -> Tuple[Quote, ...]:
        keywords = {
            word
            for keyword in keywords
            for word in keyword.split()
        }
        quotes_with_counter = set()

        for quote in quotes_set:
            words_count_mapping = [
                word in keywords
                for word in self._prepare_words_set_from_quote(quote.quote)
            ]
            quote_rating = sum(words_count_mapping)
            quotes_with_counter.add((quote_rating, quote))

        sorted_quotes = sorted(
            quotes_with_counter,
            key=lambda quote_: (quote_[0], -len(quote_[1].quote)),
            reverse=True)

        return tuple(quote for quote_rating, quote in sorted_quotes)

    def _prepare_words_set_from_quote(self, text: str) -> Set[str]:
        """
        Tokenize for getting quote words.
        :param text: str
        :return: Set of words
        """
        return {
            word
            for word in word_tokenize(text)
            if word not in self.stop_words
        }

    @staticmethod
    def _generate_key_from_string(string: str):
        return return_only_lower_letters(string.lower())
