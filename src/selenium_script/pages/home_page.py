from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.exceptions.homepage import LoginElementNotFound , LoginRedirectFailed
from src.selenium_script.script_config import config_automation as config

class HomePage:
    """ Handles all thing home page related """
    def __init__(self, driver: ChromeWebdriver):
        self.driver = driver
    
    def is_home_page(self) -> bool:
        ''' Checks if current page is home page '''
        return config.TARGET_TITLE in self.driver.title
    
    def _get_login_url(self) -> str:
        ''' 
            Extracts the url that will redirect to login page.
            Avoid's having to handle clicking an element to trigger a modal pop-up for login.
        '''
        login_class_name = 'user-data__sign'

        try:
            login_div = self.driver.find_element(By.CLASS_NAME,login_class_name)
        except NoSuchElementException as e:
            raise LoginElementNotFound(
                message= "Missing login container",
                action= 'find element by CLASS_NAME',
                selector= f"{login_class_name}"
            ) from e

        
        try:
            login_anchor = login_div.find_element(By.TAG_NAME,'a')
        except NoSuchElementException as e:
            raise LoginElementNotFound(
                message= "Missing anchor <a> element",
                action='find element by TAG_NAME',
                selector='a'
            ) from e
        
        login_url = login_anchor.get_attribute('href')
        if not login_url:
            raise LoginElementNotFound(
                message= "Missing or empty attribute 'href' .",
                action= "get_attribute",
                selector= "href"
            )
        
        return login_url
    
    def go_to_login_page(self) ->Exception | None:
        try:
            login_url = self._get_login_url()
            self.driver.get(login_url)
            return
        except LoginElementNotFound as e:
            raise LoginRedirectFailed(
                message= "Could not redirect to login landing page.",
                action= "webdriver '.get' "
            ) from e

