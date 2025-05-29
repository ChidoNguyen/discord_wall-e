from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.exceptions.script_jobs import SearchJobError
"""
Input Search Query is main job to get to "results" landing for next job role
"""

class SearchJob:
    """ Search itself does not have a 'page' to be listed under pages. Treated as a job/task instead but still wrapped into class for better context management. """
    def __init__(self, driver: ChromeWebdriver, search_query: str, max_result: int = 10):
        self.driver = driver
        self.max_results = max_result

        self.search_query = search_query

        self.search_xpath = {
            'search_field' : "//input[@id= 'searchFieldx']",
            'search_button' : "//button[@type= 'submit' and @aria-label='Search']"
        }

    def _get_search_field_elem(self) -> WebElement:
        """ Locates the search input container. """
        try:
            return self.driver.find_element(By.XPATH, self.search_xpath['search_field'])
        except NoSuchElementException as e:
            raise SearchJobError(
                message="Could not locate search field or container.",
                action=".find_element(By.XPATH)",
                selector=f"{self.search_xpath['search_field']}"
            ) from e
        
    def _input_search_query(self, input_field: WebElement) -> None:
        """ Automates entry of search query. """
        try:
            input_field.send_keys(self.search_query)
        except Exception as e:
            raise SearchJobError(
                message="Could not input search query.",
                action=".send_keys()",
            ) from e
        
    def _initiate_search(self) -> None:
        """ Automates clicking search button. """
        try:
            search_button = self.driver.find_element(By.XPATH, self.search_xpath['search_button'])
            search_button.click()
        except NoSuchElementException as e:
            raise SearchJobError(
                message="Could not locate button to initiate search.",
                action=".find_element(By.XPATH)",
                selector=f"{self.search_xpath['search_button']}"
            ) from e
        
    def perform_search(self) -> None:
        """ Automates the logic of intiating a search query. """
        search_box = self._get_search_field_elem()
        self._input_search_query(search_box)
        self._initiate_search()
        return

