from .selenium_base import SeleniumBaseException

class LoginPageElementNotFound(SeleniumBaseException):
    def __post_init__(self):
        self.module = "LoginPage"
class LoginProcedureFailed(SeleniumBaseException):
    def __post_init__(self):
        self.module = "LoginPage"
class LoginVerificationError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "LoginPage"