from .selenium_base import SeleniumBaseException

class SearchJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module = 'SearchJob'

class ResultJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module= "ResultJob"

class AcquireJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "AcquireJob"
        
class ScriptJobRunnerError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "JobWrapper"