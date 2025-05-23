from urllib.parse import urljoin

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.exceptions.result_detail import ResultDetailPageError

from src.selenium_script.script_config import config_automation as config
# XXX MIGHT NEED TO DO HUGE WAIT STUFF HERE XXX #
class ResultDetailPage:
    def __init__(self, driver: ChromeWebdriver , path: str):
        self.driver = driver
        self.details_url = urljoin(config.URL,path)
        self.prev_url = None

        self.button_selector = (By.CSS_SELECTOR ,"a.btn.btn-default.addDownloadedBook")
        
        self.download_button: WebElement | None = None

    def load(self):
        ''' saves current url and loads/sends driver to details page '''
        self.prev_url = self.driver.current_url
        self.driver.get(self.details_url)
      
    def _locate_download_button(self):
        # XXX might really need to do waits here
        try:
            self.download_button = self.driver.find_element(*self.button_selector)
        except NoSuchElementException as e:
            raise ResultDetailPageError(
                message="Could not locate download button.",
                action=f".find_element({self.button_selector[0]})",
                selector=f"[{self.button_selector[1]}]"
            )
    
    
    def _initiate_download(self):
        if not self.download_button:
            raise ResultDetailPageError(
                message="Missing download button to initiate download.",
                action="_initiate_download()"
            )
        self.download_button.click()

    
    def download(self):
        """ clicks the button """
        try:
            if not self.download_button:
                self._locate_download_button()
            self._initiate_download()
        except ResultDetailPageError as e:
            raise e
        

    