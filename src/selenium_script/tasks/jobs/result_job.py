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
    #sift through our data
    valid_result: list[WebElement] = []
    try:
        for container in data:
            if result_page.verify_container(container):
                valid_result.append(container)
    except Exception as e:
        raise SearchResultPageError(
            message="Could not validate and filter search results.",
            action="verify_container()"
        ) from e
    return valid_result

def _extract_container_url(result_page: SearchResultPage, data: list[WebElement]) -> list[str]:
    container_url: list[str] = []
    try:
        for container in data:
            container_url.append(result_page.extract_url(container))
    except Exception as e:
        raise SearchResultPageError(
            message="Failed to extract results container url.",
            action=".extract_url() and .get_attribute()",
            selector="[`href`]"
        ) from e
    return container_url

def _result_job(driver: ChromeWebdriver) -> list[str]:
    result_page = SearchResultPage(driver)
    # verify page source
    try:
        result_page.is_results_page()
    except SearchResultPageError as e:
        raise ResultJobError(
            message="Base webpage not at results webpage.",
        ) from e
    
    # populate , and assign
    try:
        result_page.locate_search_results_containers()
    except SearchResultPageError as e:
        pass
    results_containers: list[WebElement] = result_page.results_containers

    # need to filter out results to things we want.
    try:
        valid_containers = _process_result_container(result_page,results_containers)
    except SearchResultPageError as e:
        raise ResultJobError(
            message="Failed to process result containers.",
            action="_process_result_container()",
        ) from e
    
    #pull the links
    try:
        valid_result_url = _extract_container_url(result_page,valid_containers)
    except SearchResultPageError as e:
        raise ResultJobError(
            message="Failed to process results container urls.",
            action="_extract_container_url()"
        ) from e

    return valid_result_url or []

def result_job(driver: ChromeWebdriver) -> list[str]:
    try:
        result = _result_job(driver)
    except ResultJobError as e:
        raise e
    
    if not result:
        raise ResultJobError(
            message="Empty list of result urls."
        )
    return result
    