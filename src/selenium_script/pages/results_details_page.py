from urllib.parse import urljoin

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.exceptions.result_detail import ResultDetailPageError

from src.selenium_script.script_config import config_automation as config
# XXX MIGHT NEED TO DO HUGE WAIT STUFF HERE XXX #
class ResultDetailPage:
    def __init__(self, driver: ChromeWebdriver ):
        self.driver = driver
        self.base_url = (config.URL)
        self.prev_url = driver.current_url

        self.button_selector = (By.CSS_SELECTOR ,"a.btn.btn-default.addDownloadedBook")
        
        self.download_button: WebElement | None = None

    def load(self, * , details_url: str):
        ''' saves current url and loads/sends driver to details page '''
        full_url = urljoin(self.base_url, details_url)
        self.driver.get(full_url)
      
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
        

    def _get_title(self) -> str:
        title_xpath = "//h1[@itemprop= 'name']"
        try:
            title_container = self.driver.find_element(By.XPATH,title_xpath)
            title_text = title_container.text
        except NoSuchElementException as e:
            raise ResultDetailPageError(
                message="Unable to locate title container.",
                action=".find_element(By.XPATH)",
                selector=f"{title_xpath}"
            ) from e
        return title_text
    
    def _get_author(self) -> str:
        author_xpath = '//a[@class= "color1"][@title="Find all the author\'s book"]'
        try:
            author_container = self.driver.find_element(By.XPATH,author_xpath)
            author_text = author_container.text
        except NoSuchElementException as e:
            raise ResultDetailPageError(
                message="Unable to locate author container.",
                action=".find_element(By.XPATH)",
                selector=f"{author_xpath}"
            ) from e
        return author_text
    
    def _build_data_detail(self) -> dict[str,str]:
        title = self._get_title()
        author = self._get_author()
        return { 'link' : self.driver.current_url , 'author' : author , 'title' : title}
    
    def get_results_details(self) -> dict[str,str]:
        return self._build_data_detail()
