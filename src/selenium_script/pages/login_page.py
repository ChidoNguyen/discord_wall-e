from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

class LoginPage:
    login_form: WebElement

    def __init__(self,driver: ChromeWebdriver):
        self.driver = driver

    def is_login_page(self) -> bool:
        login_form_tag = 'form'
        try:
            self.login_form = self.driver.find_element(By.TAG_NAME,login_form_tag)
            return True
        except NoSuchElementException:
            return False
    
    def _input_id(self,user_id: str):
        try:
            self.login_form.find_element(By.NAME, 'email').send_keys(user_id)
        except NoSuchElementException:
            return None
    
    def _input_pass(self, password: str):
        try:
            self.login_form.find_element(By.NAME, 'password').send_keys(password)
        except NoSuchElementException:
            return None
    def valid_login(self):
        logout_xpath = "//a[@href='/logout']"
        try:
            self.driver.find_element(By.XPATH,logout_xpath)
            return True
        except NoSuchElementException:
            return False
        
    def perform_login(self,username:str,password:str):
        try:
            self._input_id(username)
            self._input_pass(password)
        except Exception as e:
            raise NoSuchElementException(f"Input Error - {e}") from e
        
        try:
            self.login_form.find_element(By.TAG_NAME,'button').click()
        except NoSuchElementException as e:
            raise NoSuchElementException("Could not click form submit/login button.")
        

        


        