from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config
class HomePage:

    def __init__(self, driver: ChromeWebdriver):
        self.driver = driver
    
    def is_home_page(self) -> bool:
        return config.TARGET_TITLE in self.driver.title
    
    def _get_login_url(self) -> str:
        login_class_name = 'user-data__sign'

        try:
            login_div = self.driver.find_element(By.CLASS_NAME,login_class_name)
        except NoSuchElementException as e:
            raise NoSuchElementException(f"Login container with class identifier {login_class_name} could not be found.  [Original Error : {e}]") from e
        
        try:
            login_anchor = login_div.find_element(By.TAG_NAME,'a')
        except NoSuchElementException as e:
            raise NoSuchElementException(f"Login anchor <a> element could not be found. - [Original Error : {e}]") from e
        
        login_url = login_anchor.get_attribute('href')
        if not login_url:
            raise NoSuchElementException("Login anchor found, but missing/empty href attributes.")
        
        return login_url
    
    def go_to_login_page(self) ->tuple[bool,str]:
        try:
            login_url = self._get_login_url()
            self.driver.get(login_url)
            return True , ""
        except Exception as e:
            return False , str(e)
