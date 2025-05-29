from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement

#page/ui handler
from src.selenium_script.pages.search_results_page import SearchResultPage

def _process_result_container(result_page: SearchResultPage, data: list[WebElement]) -> list[WebElement]:
    """ 
    Filters clist of container web elements
    
    Args:
        result_page: UI/Page class handler
        data (list[WebElement]): list of WebElements
    
    Returns:
        list[WebElement]
    
    Raises:
        SearchResultPageError - bubbled up from .verify_container() if fail 
    """
    return [ container for container in data if result_page.verify_container(container)]

def _extract_container_url(result_page: SearchResultPage, data: list[WebElement]) -> list[str]:
    """ Extracts url from list of WebElements.
    
        Returns:
            list[str]

        Raises:
            SearchResultPageError - bubbled up from .extract_url() if fail
    """
    return [ result_page.extract_url(container) for container in data ]

def result_job(driver: ChromeWebdriver) -> list[str]:
    """
    Leaned out logic flow to perform `result_job`.

    Args:
        driver (ChromeWebDriver): Instance of web driver

    Returns:
        list[str] containing urls related to valid search results
    
    Raises:
        All Errors are allowed to bubble up from lower level function calls. Handled in the `task layer` handlers.

        SearchResultPageError

    """
    result_page = SearchResultPage(driver)
    result_page.is_results_page()
    result_page.locate_search_results_containers()
    result_containers = result_page.results_containers
    valid_containers = _process_result_container(result_page,result_containers)
    return _extract_container_url(result_page,valid_containers)
    