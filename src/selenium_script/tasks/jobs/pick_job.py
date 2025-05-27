from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from src.selenium_script.script_config import config_automation as config

from src.selenium_script.exceptions.pick_choice import ChoiceCreationJobError


def create_options_job(*,driver: ChromeWebdriver, results: list[str]):
    pass