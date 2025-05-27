from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from src.selenium_script.exceptions.login_page import LoginPageElementNotFound, LoginProcedureFailed,LoginVerificationError
class LoginPage:
    login_form: WebElement

    def __init__(self,driver: ChromeWebdriver):
        self.driver = driver

    def is_login_page(self) -> bool:
        # XXX Need a better check ###
        login_form_tag = 'form'
        try:
            self.login_form = self.driver.find_element(By.TAG_NAME,login_form_tag)
            return True
        except NoSuchElementException:
            raise LoginPageElementNotFound(
                message= "Could not confirm login form presence.",
                action= "find element by TAG_NAME",
                selector= f"{login_form_tag}"
            )
    
    def _input_id(self,user_id: str) -> None:
        try:
            self.login_form.find_element(By.NAME, 'email').send_keys(user_id)
        except NoSuchElementException:
            raise LoginPageElementNotFound(
                message="Could not find or input into email field.",
                action="find element and send keys",
                selector="email"
            )
    
    def _input_pass(self, password: str):
        try:
            self.login_form.find_element(By.NAME, 'password').send_keys(password)
        except NoSuchElementException:
            raise LoginPageElementNotFound(
                message= "Could not find or input into password field.",
                action="find element and send keys",
                selector= "password"
            )
        
    def valid_login(self) -> bool:
        logout_xpath = "//a[@href='/logout']"
        try:
            self.driver.find_element(By.XPATH,logout_xpath)
            return True
        except NoSuchElementException:
            raise LoginVerificationError(
                message="Could not verify successful login state.",
                action="find element by XPATH",
                selector=f"logout xpath : {logout_xpath}"
            )
        
    def login(self,username:str,password:str):
        try:
            self._input_id(username)
            self._input_pass(password)
            self.login_form.find_element(By.TAG_NAME,'button').click()
        except LoginPageElementNotFound as e:
            raise LoginProcedureFailed(
                message= f"{e}",
                action='performing login logic'
            ) from e
        except NoSuchElementException as e:
            raise LoginProcedureFailed(
                message="Could not locate form submission button",
                action="find element and click",
                selector="button"
            ) from e

        

        


        