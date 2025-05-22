from .selenium_base import SeleniumBaseException

class SearchResultPageError(SeleniumBaseException):
    def __post_init__(self):
        self.module = 'SearchResultPage'
        