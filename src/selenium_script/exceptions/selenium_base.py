from dataclasses import dataclass , field

@dataclass
class SeleniumBaseException(Exception):
    '''
        A generic exception template for project's selenium scripts

        message - What
        module - Where
        action - How
        selector - Who
    '''
    message : str
    action : str | None = None
    selector : str | None = None
    module: str = field(default='Unknown',init=False)

    def __str__(self):
        return (
            f"[{self.module}] {self.message} |"
            f"{f'[Action] {self.action} |' if self.action else ''}"
            f"{f'[Selector] {self.selector} |' if self.action else ''}"
        )