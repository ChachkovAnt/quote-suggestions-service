from dataclasses import dataclass
from typing import Optional

from quotes_suggestions_service.utils.base import StringEnum

from .enums import WikiAction, WikiResponseFormat


@dataclass
class WikiUrlParametersDTO:

    action: WikiAction
    format: WikiResponseFormat = WikiResponseFormat.JSON
    page: Optional[str] = None
    search: Optional[str] = None
    limit: Optional[int] = None

    def __post_init__(self):
        if self.action is WikiAction.OPENSEARCH:
            assert self.search is not None, self.parameter_not_passed_error('search', self.action)
            assert self.page is None, self.parameter_passed_error('page', self.action)

        if self.action is WikiAction.PARSE:
            assert self.page is not None, self.parameter_not_passed_error('page', self.action)
            assert self.search is None, self.parameter_passed_error('search', self.action)
            assert self.limit is None, self.parameter_passed_error('limit', self.action)

    def mapping(self):
        return {
            parameter: value.value if isinstance(value, StringEnum) else value
            for parameter, value in self.__dict__.items()
            if value is not None
        }

    @staticmethod
    def parameter_passed_error(parameter: str, action: WikiAction):
        return f"'{parameter}' parameter shouldn't be passed when action is '{action.value}'"

    @staticmethod
    def parameter_not_passed_error(parameter, action):
        return f"'{parameter}' parameter should be passed when action is '{action.value}'"
