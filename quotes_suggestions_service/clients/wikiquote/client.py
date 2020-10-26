import re
from typing import Iterable, Tuple, List, Set, Union
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup, Tag, NavigableString

from quotes_suggestions_service.utils import NAME_VALIDATORS_MAPPING
from quotes_suggestions_service.utils.enums import Localization

from .constants import EN_EXTRA_BLOCKS_NAMES, EN_QUOTES_BLOCK_NAME
from .enums import WikiAction, WikiResponseFormat
from .dtos import WikiUrlParametersDTO
from ..dtos import Quote
from ..base import QuotesApiClient


class WikiQuoteClient(QuotesApiClient):
    """
    Multi-language client
    """

    LOCALIZATION: Localization = None
    api_url: str = None

    def __init__(self, localization: Localization):
        self.LOCALIZATION = localization
        self.api_url = f'https://{localization.value}.wikiquote.org/w/api.php'

        self.validator = NAME_VALIDATORS_MAPPING[localization]

    def get_quotes(self, authors: Iterable[str], keywords: Iterable[str]) -> Tuple[Quote, ...]:
        # Wiki client can to search only by name at the moment
        raw_responses = (
            self._get_data(
                WikiUrlParametersDTO(
                    action=WikiAction.PARSE,
                    page=author,
                    format=WikiResponseFormat.JSON))
            for author in authors)

        quotes = tuple(
            quote
            for title, page in raw_responses
            if page is not None
            for quote in self._parse_quotes(title, page)
        )

        return quotes

    def _get_data(
            self,
            url_parameters: WikiUrlParametersDTO) \
            -> Tuple[Union[str, None], Union[str, None]]:
        """
        :return: (page title, raw page data)
        """
        decoded_response = requests.get(
            self.api_url, params=url_parameters.mapping()).json()

        if self._is_error(decoded_response):
            return None, None

        if self._is_redirect(decoded_response):
            redirect_page_name = BeautifulSoup(
                decoded_response['parse']['text']['*'], features="html.parser") \
                .find('a') \
                .get('href') \
                .split('/')[-1]

            url_parameters.page = unquote(redirect_page_name)
            decoded_response = requests.get(
                self.api_url, params=url_parameters.mapping()).json()

        return decoded_response['parse']['title'], decoded_response['parse']['text']['*']

    @staticmethod
    def _is_redirect(response) -> bool:
        if isinstance(response, dict):
            return "redirectMsg" in response['parse']['text']['*']

    @staticmethod
    def _is_error(response) -> bool:
        if isinstance(response, dict):
            return bool(response.get('error'))

    def _parse_quotes(self, title: str, raw_response: str) -> Set[Quote]:
        if not self.validator.is_person(title):
            return set()

        soup = BeautifulSoup(raw_response, 'html.parser') \
            .find('div', {'class': 'mw-parser-output'})

        # Remove links
        for a in soup.find_all('a', href=True):
            if bool(re.match(r'\[\d*]', str(a.string))):
                a.extract()
            elif a.string is not None:
                a.insert_after(a.string)
            a.extract()
        [sup.extract() for sup in soup.find_all('sup')]

        # Some quotes are marked as <div class="poem">, it's make sense to unpack them here
        poem_class_quotes = self._parse_page_with_poem_class_tags(title, soup)
        li_tags_quotes = self._parse_page_with_li_tags(title, soup)

        quotes = {*li_tags_quotes, *poem_class_quotes}

        return quotes

    def _parse_page_with_li_tags(self, page_title: str, soup: BeautifulSoup) -> List[Quote]:
        # Remove extra highlighted blocks like Disputed, Misattributed..
        for block_name in EN_EXTRA_BLOCKS_NAMES:
            excess_block = soup.find(text=block_name)
            if excess_block is not None:
                excess_block.find_parent('div').extract()

        # Search only necessary blocks
        raw_quotes = []
        h2 = soup.find('span', text=re.compile(EN_QUOTES_BLOCK_NAME)).parent
        tags = h2.find_next_siblings()
        for tag in tags:
            if tag.name == 'h2':
                break
            # Exclude h3, h4, dl, p tags
            if tag.name not in ('h3', 'h4', 'dl', 'p', 'div'):
                raw_quotes.append(tag)

        quotes = []
        for num, tag in enumerate(raw_quotes):
            quote = None
            description = None
            # Replace <br> tags to \n symbols
            for tag_ in tag.find_all('br'):
                tag_.insert_after('\n')
                tag_.extract()

            if tag.name == 'ul':
                if len(tag.li.contents) < 3:
                    quote = tag.li.contents[0]
                    if isinstance(quote, Tag):
                        quote = quote.text

                    description = tag.li.contents[1] if len(tag.li.contents) > 1 else None
                    if isinstance(description, Tag):
                        description = description.text
                else:
                    if len(tag.find_all('li')) == 1:
                        quote = tag.text
                        description = None
                    else:
                        try:
                            description = tag.li.contents[-1].extract().text
                            quote = tag.text
                        except AttributeError:
                            # TEMPORARY: Ignore all `unparsable` quotes
                            continue

            elif tag.name == 'li':
                quote = tag.li.text

            if quote is not None:
                if isinstance(quote, NavigableString):
                    quote = str(quote)
                if isinstance(description, NavigableString):
                    description = str(description)

                quote = Quote(
                    quote=self._prettify_string(quote),
                    author=page_title,
                    description=self._prettify_string(description)
                    if description is not None else None)

                quotes.append(quote)

        return quotes

    def _parse_page_with_poem_class_tags(
            self, page_title: str, soup: BeautifulSoup) -> List[Quote]:
        quotes = []

        tables = soup.find_all('div', {'class': 'poem'})

        for table in tables:
            description = table.find('span')

            if description is not None:
                description.extract()
                description = description.string

            quote = table.getText()

            quotes.append(
                Quote(
                    quote=self._prettify_string(quote),
                    author=page_title,
                    description=self._prettify_string(description)))

        return quotes

    @staticmethod
    def _prettify_string(string: str) -> Union[str, None]:
        while string.startswith('\n'):
            string = string[1:]
            if string is None:
                break

        while string.endswith('\n') or string.endswith('—') or string.endswith(' '):
            string = string[:-1]
            if string is None:
                break

        if string == '':
            return None

        return string
