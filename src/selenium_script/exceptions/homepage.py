from .selenium_base import SeleniumBaseException

class LoginElementNotFound(SeleniumBaseException):
    def __post_init__(self):
        self.module = "HomePage"
class LoginRedirectFailed(SeleniumBaseException):
    def __post_init__(self):
        self.module = "HomePage"
