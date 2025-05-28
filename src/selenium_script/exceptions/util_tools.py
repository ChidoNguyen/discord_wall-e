from .selenium_base import SeleniumBaseException

class DownloadUtilError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "DownloadUtility"

class EpubToolsError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "EpubTools"