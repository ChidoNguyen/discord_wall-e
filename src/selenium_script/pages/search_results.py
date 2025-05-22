from urllib.parse import urljoin

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.script_config import config_automation as config
from src.selenium_script.exceptions.search_results import SearchResultPageError

class SearchResultPage:
    

    def __init__(self, driver: ChromeWebdriver):
        self.driver = driver
        self.base_url = config.URL
        self.search_results: list[WebElement] = []
        self.valid_results: list[str] = []
        self.selectors={
            'title_text' : 'search on',
            'search_css_selector' : "body.search.super-puper-main-container"
        }
        self._first_run = True

    def _is_search_page(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.selectors['search_css_selector'])
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate page identifier.",
                action=".find_element(By.CSS_SELECTOR)",
                selector=f"{self.selectors['search_css_selectors']}"
            ) from e
        
    def is_results_page(self):
        self._is_search_page()

    def _get_search_results_containers(self):
        """ Gets the container that will have all the details for each individual search result component/item/container """
        info_card_class_name = 'z-bookcard'
        try:
            self.search_results = self.driver.find_elements(By.CLASS_NAME,info_card_class_name)
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate search result card/container information.",
                action=".find_elements(By.CLASS_NAME)",
                selector=f"{info_card_class_name}"
            ) from e
        
    def _verify_format(self, result: WebElement) -> bool:
        main_format = 'epub'
        result_ext = (result.get_attribute('extension') or "").lower()
        return main_format == result_ext
        
    def _verify_language(self, result: WebElement) -> bool:
        main_language = 'english'
        result_lang = (result.get_attribute('language') or "").lower()
        return main_language == result_lang
        
    def _get_result_url(self, result: WebElement) -> str:
        return result.get_attribute('href') or ""
    
    def _process_search_items(self):
        #need to check the info of each result for things we want
        # file format and language
        for item in self.search_results:
            if self._verify_format(item) and self._verify_language(item):
                self.valid_results.append(urljoin(self.base_url, self._get_result_url(item)))
            
    def perform_search(self):
        try:
            self._get_result_url
            self._process_search_items
        except SearchResultPageError as e:
            raise SearchResultPageError(
                message="could not finialize search operations",
                action="perform_search"
            ) from e
        
    def get_search_results(self) -> list[str]:
        try:
            if self._first_run:
                self.perform_search()
            return self.valid_results
        except Exception as e:
            raise SearchResultPageError(
                message="Could not retrieve search results",
                action="get_search_results"
            )from e
        






