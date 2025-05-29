from .selenium_base import SeleniumBaseException

class CookiesUtilityError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "CookiesUtil"