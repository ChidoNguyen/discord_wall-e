from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.script_config import config_automation as config

from src.selenium_script.pages.search_results import SearchResultPage

from src.selenium_script.exceptions.script_jobs import ResultJobError
from src.selenium_script.exceptions.search_results import SearchResultPageError


### Results landing page  handler ###
### Core job -> aggregate search results ###

def result_job(driver: ChromeWebdriver):
    result_page = SearchResultPage(driver)
    try:
        result_page.is_results_page()
    except SearchResultPageError as e:
        raise ResultJobError(
            message="Base page not on results page.",
        ) from e
    pass