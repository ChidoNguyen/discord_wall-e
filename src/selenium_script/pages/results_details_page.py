from urllib.parse import urljoin

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By

#Exceptions
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.exceptions.result_detail import ResultDetailPageError
#config
from src.selenium_script.script_config import config_automation as config
# XXX MIGHT NEED TO DO HUGE WAIT STUFF HERE XXX #
class ResultDetailPage:
    def __init__(self, driver: ChromeWebdriver ):
        self.driver = driver
        self.base_url = (config.URL)
        self.prev_url = driver.current_url

        self.button_selector = (By.CSS_SELECTOR ,"a.btn.btn-default.addDownloadedBook")
        self.author_xpath = '//a[@class= "color1"][@title="Find all the author\'s book"]'
        self.title_xpath = "//h1[@itemprop= 'name']"

        

    def load(self, * , details_url: str):
        ''' saves current url and loads/sends driver to details page '''
        full_url = urljoin(self.base_url, details_url)
        self.driver.get(full_url)
        if full_url != self.driver.current_url:
            raise ResultDetailPageError(
                message="Could not navigate to new url",
                action="web driver .get() ",
                selector=f"target url: [{full_url}]"
            )
        
      
    def _locate_download_button(self):
        # XXX might really need to do waits here
        try:
            return self.driver.find_element(*self.button_selector)
        except NoSuchElementException as e:
            raise ResultDetailPageError(
                message="Could not locate download button.",
                action=f".find_element({self.button_selector[0]})",
                selector=f"[{self.button_selector[1]}]"
            )

    
    def download(self):
        """ clicks the button """
        download_button = self._locate_download_button()
        download_button.click()

    def _get_detail_text(self, by: str, value: str) -> str:
        """ Re-usable .find_element wrapper to extract text.  Normalized the exception raising format template when elements are missing.
        """
        try:
            detail_container = self.driver.find_element(by,value)
            detail_text = detail_container.text
            return detail_text
        except NoSuchElementException as e:
            raise ResultDetailPageError(
                message="Unable to locate detail's container.",
                action="_get_detail_text()",
                selector=f"By: {by} Value: {value}"
            ) from e
        
    def _get_title(self) -> str:
        return self._get_detail_text(By.XPATH,self.title_xpath)
    
    def _get_author(self) -> str:
        return self._get_detail_text(By.XPATH,self.author_xpath)
    
    def _get_field(self, identifier: str) -> str:
        """ defaults xpath usage for getting field item's text"""
        return self._get_detail_text(By.XPATH,identifier)
    
    def _build_data_detail(self) -> dict[str,str]:
        fields = {
            'title' : self.title_xpath,
            'author' : self.author_xpath
        }
        return { 
            'link' : self.driver.current_url , 
            **{ k : self._get_field(v) for k,v in fields.items()} # sets our key: value relation , and then expands
        }
    
    def get_results_details(self) -> dict[str,str]:
        return self._build_data_detail()
