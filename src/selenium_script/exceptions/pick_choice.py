from src.selenium_script.exceptions.selenium_base import SeleniumBaseException

class ChoiceCreationJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module = "ChoiceCreation"

class ChoiceSelectionJobError(SeleniumBaseException):
    def __post_init__(self):
        self.module= "ChoiceSelection"