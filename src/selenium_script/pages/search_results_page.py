from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


from src.selenium_script.exceptions.search_results import SearchResultPageError

class SearchResultPage:
    def __init__(self, driver: ChromeWebdriver):
        self.driver = driver
        self.results_containers: list[WebElement] = []
        self.selectors={
            'title_text' : 'search on',
            'search_css_selector' : "body.search.super-puper-main-container"
        }

  
    def _is_search_page(self):
        """ Verifies driver is currently on a page view with search results available. """
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.selectors['search_css_selector'])
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate page identifier.",
                action=".find_element(By.CSS_SELECTOR)",
                selector=f"{self.selectors['search_css_selectors']}"
            ) from e
        
    def is_results_page(self):
        """ external facing function for page/url confirmation """
        self._is_search_page()

    def locate_search_results_containers(self):
        """ Gets the container that will have all the details for each individual search result component/item/container """
        info_card_class_name = 'z-bookcard'
        try:
            self.results_containers = self.driver.find_elements(By.CLASS_NAME,info_card_class_name)
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate search result card/container information.",
                action=".find_elements(By.CLASS_NAME)",
                selector=f"{info_card_class_name}"
            ) from e
        
    def _verify_format(self, result: WebElement) -> bool:
        ''' checks for epub file format '''
        main_format = 'epub'
        result_ext = (result.get_attribute('extension') or "").lower()
        return main_format == result_ext
        
    def _verify_language(self, result: WebElement) -> bool:
        ''' checks for english language format '''
        main_language = 'english'
        result_lang = (result.get_attribute('language') or "").lower()
        return main_language == result_lang
        
    def extract_url(self, result: WebElement) -> str:
        ''' extracts url/str value in `href` attribute '''
        return result.get_attribute('href') or ""
    
    def verify_container(self, in_question: WebElement) -> bool:
        """ checks that the container ( the result ) has key items we want. """
        return self._verify_format(in_question) and self._verify_language(in_question)





