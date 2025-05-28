from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.exceptions.homepage import LoginElementNotFound , LoginRedirectFailed
from src.selenium_script.script_config import config_automation as config

class HomePage:
    """ 
    Handles all thing home page UI related. 

    Args:
        driver (ChromeWebDriver): instance of selenium chrome webdriver
    
    """

    def __init__(self, driver: ChromeWebdriver):
        self.driver = driver
    
    def is_home_page(self) -> bool:
        """ Verifies driver is on home page based on defined target identifiers. """
        return config.TARGET_TITLE in self.driver.title
    
    def get_login_container(self) -> WebElement:
        """ Locates login container element based on class name signature provided. """
        container_class_name = 'user-data__sign'
        try:
            return self.driver.find_element(By.CLASS_NAME, container_class_name)
        except NoSuchElementException as e:
            raise LoginElementNotFound(
                message="Could not locate login container.",
                action="find_element by CLASS_NAME",
                selector=f"{container_class_name}"
            ) from e
    
    def get_login_anchor(self, login_container: WebElement) -> WebElement:
        """ Locates the anchor element inside a container. """
        anchor_tag = 'a'
        try:
            return login_container.find_element(By.TAG_NAME, anchor_tag)
        except NoSuchElementException as e:
            raise LoginElementNotFound(
                message= "Could not locate anchor in login container.",
                action='find_element by TAG_NAME',
                selector='a'
            ) from e
    
    def get_login_href(self, login_anchor_element: WebElement) -> str:
        """ Extracts the url string stored in the href attribute of a container. """
        href_url = login_anchor_element.get_attribute('href')
        if not href_url:
            raise LoginElementNotFound(
                message= "Missing or empty attribute 'href' .",
                action= "get_attribute",
                selector= "href"
            )
        return href_url
        
        
    def get_login_url(self) -> str:
        """ Returns the url necessary to get to login landing page. """
        login_div = self.get_login_container()
        login_anchor = self.get_login_anchor(login_div)
        return self.get_login_href(login_anchor)


