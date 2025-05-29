from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.exceptions.download_history import DownloadHistoryElementError

class DownloadHistory:
    def __init__(self , driver : ChromeWebdriver):
        self.driver = driver

        self._url_history = driver.current_url
        self.visit_history = False

        self._download_limit_container: WebElement
        self._download_count : int = -1
        self._max_download : int = -1

    def _go_back(self):
        self.driver.get(self._url_history)

    def _go_to_history(self) -> None:
        """ Navigates script/bot to download history. """
        history_elem_xpath = "//a[@href='/users/downloads']"
        try:
            container = self.driver.find_element(By.XPATH, history_elem_xpath)
            download_history_url = container.get_attribute('href')
        except NoSuchElementException as e:
            raise DownloadHistoryElementError(
                message="Missing history element container.",
                action="find element By.XPATH",
                selector=f"[{history_elem_xpath}]"
            ) from e
        if not download_history_url:
            raise DownloadHistoryElementError(
                message="Invalid download history url.",
                action=".get_attribute",
                selector="href"
            )
        self.driver.get(download_history_url)

    def _verify_on_history(self) -> None:
        ''' Checks for download history page identifiers '''
        download_limit_css = "div.m-v-auto.d-count"
        
        try:
            self._download_limit_container = self.driver.find_element(By.CSS_SELECTOR, download_limit_css)
        except NoSuchElementException as e:
            raise DownloadHistoryElementError(
                message="Missing download history css identifier",
                action="find element by CSS_SELECTOR",
                selector=f"[{download_limit_css}]"
            ) from e
        
    def _get_limit_info(self) -> None:
        """
        gather information about download limit/ capacity.

        """
        current_limit_text = self._download_limit_container.text.strip()
        #split the string with /
        download_text_info= current_limit_text.split('/') 
        if len(download_text_info) != 2:
            raise DownloadHistoryElementError(
                message="Unexpected format in download history text.",
                action="split on '/' "
            )
        try:
            self._download_count = int(download_text_info[0])
            self._max_download = int(download_text_info[1])
        except Exception as e:
            raise DownloadHistoryElementError(
                message="Failed to parse integers from download text string split.",
                action="int() casting."
            ) from e
        
        if self._download_count < 0 or self._max_download < 0:
            raise DownloadHistoryElementError(
                message="Invalid parsed download information values."
            )

    def refresh(self) -> None:
        """ forces a refresh if we need new dl information """
        self._visit_history = False
        self.go_to_history()

    def go_to_history(self):
        try:
            self._go_to_history() # moves us to dl history
            self._verify_on_history() #verify proper page
            self._get_limit_info() # get our information
            self._go_back() # sends us back to our starting point
            self.visit_history = True
        except Exception as e:
            raise DownloadHistoryElementError(
                message=f"{e}",
            ) from e
        
    @property
    def download_count(self) -> int:
        if not self.visit_history:
            self.go_to_history()
        return self._download_count
    @property
    def max_download(self) -> int:
        if not self.visit_history:
            self.go_to_history()
        return self._max_download
    