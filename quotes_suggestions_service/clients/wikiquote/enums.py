from quotes_suggestions_service.utils.base import StringEnum


class WikiResource(StringEnum):

    WIKIPEDIA = 'wikipedia'
    WIKIQUOTE = 'wikiquote'


class WikiAction(StringEnum):

    QUERY = 'query'
    PARSE = 'parse'
    OPENSEARCH = 'opensearch'


class WikiResponseFormat(StringEnum):

    JSON = 'json'
    XML = 'xml'
    PHP = 'php'
    RAWFM = 'rawfm'
    NONE = 'none'
