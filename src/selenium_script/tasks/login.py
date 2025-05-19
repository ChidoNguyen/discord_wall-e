from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from pages.homepage import HomePage
from pages.login_page import LoginPage

from exceptions.homepage import LoginRedirectFailed
from exceptions.login_page import LoginPageElementNotFound, LoginProcedureFailed, LoginVerificationError

def perform_login(driver : ChromeWebdriver) -> tuple[bool,str|Exception]:
    home = HomePage(driver)
    if not home.is_home_page():
        return False , NoSuchElementException("Missing home page elements.")
    
    #go to login url
    try:
        home.go_to_login_page()
    except LoginRedirectFailed as e:
        return False , e
    
    login_page = LoginPage(driver)
    try:
        login_page.is_login_page()
    except LoginPageElementNotFound as e:
        return False, e
   
    
    try:
        login_page.perform_login(config.ACCOUNTS[0],config.PASSWORD)
    except LoginProcedureFailed as e:
        return False , e
    
    try:
        login_page.valid_login()
    except LoginVerificationError as e:
        return False, e
    
    return True,''
