from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


from src.selenium_script.exceptions.search_results import SearchResultPageError

class SearchResultPage:
    """ 
    Handles search result page ui items. 

    Initialize with web driver and our desired file formats to check for later if needed.

    Args: 
        driver (chrome driver): selenium web driver instance
        format and language (str): desired search result attributes
    """
    def __init__(self, driver: ChromeWebdriver , format: str = 'epub', language: str = 'english'):
        self.driver = driver
        self.desired_format = format.lower()
        self.desired_language = language.lower()
        self.results_containers: list[WebElement] = []
        self.selectors={
            'title_text' : 'search on',
            'search_css_selector' : "body.search.super-puper-main-container"
        }

  
    def is_results_page(self):
        """ Verifies driver is currently on a page view with search results available. """
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.selectors['search_css_selector'])
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate page identifier.",
                action=".find_element(By.CSS_SELECTOR)",
                selector=f"{self.selectors['search_css_selectors']}"
            ) from e

    def locate_search_results_containers(self):
        """ Gets the container that will have all the details for each individual search result component/item/container """
        info_card_class_name = 'z-bookcard'
        try:
            self.results_containers = self.driver.find_elements(By.TAG_NAME,info_card_class_name)
        except NoSuchElementException as e:
            raise SearchResultPageError(
                message="Could not locate search result card/container information.",
                action=".find_elements(By.CLASS_NAME)",
                selector=f"{info_card_class_name}"
            ) from e
        
    def _verify_attribute(self, result: WebElement, attr: str):
        """ 
        Verifies that designated attribute is present in the webelement.
        
        Raises:
            SearchResultPageError (custom exception) : if attribute is missing.
        """  
        attr_value = result.get_attribute(attr)
        if attr_value is None:
            raise SearchResultPageError(
                message="Missing required attribute.",
                action="get_attribute",
                selector=attr
            )
        return attr_value 
    
    def _verify_format(self, result: WebElement) -> bool:
        ''' checks for epub file format '''
        attr_key = 'extension'
        result_ext = self._verify_attribute(result,attr_key)
        return self.desired_format == result_ext.lower()
        
    def _verify_language(self, result: WebElement) -> bool:
        ''' checks for english language format '''
        attr_key = 'language'
        result_lang = self._verify_attribute(result,attr_key)
        return self.desired_language == result_lang.lower()
    
    def extract_url(self, result: WebElement) -> str:
        ''' extracts url/str value in `href` attribute '''
        # href is str or none , no desired check needed.
        return self._verify_attribute(result,'href')
    
    def verify_container(self, in_question: WebElement) -> bool:
        """ checks that the container ( the result ) has key items we want. """
        return self._verify_format(in_question) and self._verify_language(in_question)





