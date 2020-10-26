from typing import Tuple, Set

import requests
from requests import Response
from bs4 import BeautifulSoup

from quotes_suggestions_service.utils import NAME_VALIDATORS_MAPPING
from quotes_suggestions_service.utils.enums import Localization

from ..dtos import Quote
from ..base import QuotesApiClient


class BrainyQuoteClient(QuotesApiClient):
    """
    Single-language (EN) client
    """

    api_url = 'https://www.brainyquote.com'
    topics_url = f'{api_url}/topics'
    authors_url = f'{api_url}/authors'
    validator = NAME_VALIDATORS_MAPPING[Localization.ENGLISH]

    def get_quotes(self, authors: Tuple[str], keywords: Tuple[str]) -> Set[Quote]:
        if len(authors) != 0:
            quotes = set(
                quote
                for author in authors
                for quote in self._get_quotes_by_author(author))
        elif len(authors) == 0 and len(keywords) != 0:
            quotes = set(
                quote
                for keyword in keywords
                for quote in self._get_keyword_quotes(keyword))
        else:
            raise ValueError("At least one of argument should be passed")

        return quotes

    def _get_quotes_by_author(self, author: str) -> Tuple[Quote, ...]:
        prepared_name = '-'.join(author.lower().split())
        pages = self._get_paginated_pages(f'{self.authors_url}/{prepared_name}')

        return self._parse_quotes_from_pages(pages)

    def _get_keyword_quotes(self, keyword: str) -> Tuple[Quote, ...]:
        if self.validator.is_person(keyword):
            quotes = self._get_quotes_about_person(keyword)
        else:
            quotes = self._get_quotes_by_keyword(keyword)

        return quotes

    def _get_quotes_about_person(self, person_name: str) -> Tuple[Quote, ...]:
        person_name = person_name.lower().replace('about', '').split()
        prepared_name = '-'.join(person_name)
        pages = self._get_paginated_pages(f'{self.topics_url}/{prepared_name}')

        return self._parse_quotes_from_pages(pages)

    def _get_quotes_by_keyword(self, keyword: str) -> Tuple[Quote, ...]:
        prepared_keyword = '-'.join(keyword.lower().split())
        pages = self._get_paginated_pages(f'{self.topics_url}/{prepared_keyword}')

        return self._parse_quotes_from_pages(pages)

    def _get_paginated_pages(self, url: str) -> Tuple[Response, ...]:
        first_page = requests.get(url)
        # Find all pages links on the first page pagination and exclude `Next` link
        pagination_tag = BeautifulSoup(first_page.text, 'html.parser') \
            .find('ul', {'class': 'pagination'})

        pages_paths = [
            a['href'] for a in pagination_tag.find_all('a', href=True)
        ] if pagination_tag is not None else []

        rest_pages = (
            requests.get(self.api_url + path)
            for path in pages_paths[:-1]  # Without `Next` link
        )

        return first_page, *rest_pages

    @staticmethod
    def _parse_quotes_from_pages(pages: Tuple[Response]) -> Tuple[Quote, ...]:
        raw_quotes_list = [
            BeautifulSoup(page.text, 'html.parser').find_all('div', {'class': 'clearfix'})
            for page in pages
        ]

        return tuple(
            Quote(
                quote=raw_quote.find('a', {'title': 'view quote'}).text,
                author=raw_quote.find('a', {'title': 'view author'}).text)
            for raw_quotes in raw_quotes_list for raw_quote in raw_quotes)
