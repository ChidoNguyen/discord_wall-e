from .selenium_base import SeleniumBaseException

class DownloadHistoryElementError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "DownloadHistory"