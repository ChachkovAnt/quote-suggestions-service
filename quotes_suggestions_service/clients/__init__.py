from .wikiquote import WikiQuoteClient
from .brainyquote import BrainyQuoteClient
from quotes_suggestions_service.utils.enums import Localization


EN_QUOTES_API_CLIENTS = (
    WikiQuoteClient(Localization.ENGLISH), BrainyQuoteClient(),
)

# Not implemented
# RU_QUOTES_API_CLIENTS = (WikiQuoteClient(Localization.RUSSIAN), )
