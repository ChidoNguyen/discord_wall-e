from .selenium_base import SeleniumBaseException

class ResultDetailJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module="ResultDetailJob"
        
class ResultDetailPageError(SeleniumBaseException):
    def __post_init__(self):
        self.module="ResultDetailPage"
