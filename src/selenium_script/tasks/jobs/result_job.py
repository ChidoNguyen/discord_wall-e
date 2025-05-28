from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.script_config import config_automation as config

from src.selenium_script.pages.search_results_page import SearchResultPage

from src.selenium_script.exceptions.script_jobs import ResultJobError
from src.selenium_script.exceptions.search_results import SearchResultPageError


### Results landing page  handler ###
### Core job -> aggregate search results ###
def _process_result_container(result_page: SearchResultPage, data: list[WebElement]) -> list[WebElement]:
    # filter down our data to valid results only
    return [ container for container in data if result_page.verify_container(container)]

def _extract_container_url(result_page: SearchResultPage, data: list[WebElement]) -> list[str]:
    return [ result_page.extract_url(container) for container in data ]

def result_job(driver: ChromeWebdriver) -> list[str]:
    result_page = SearchResultPage(driver)
    result_page.is_results_page()
    result_page.locate_search_results_containers()
    result_containers = result_page.results_containers
    valid_containers = _process_result_container(result_page,result_containers)
    return _extract_container_url(result_page,valid_containers)
    