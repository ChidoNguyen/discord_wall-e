from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from src.selenium_script.pages.homepage import HomePage
from src.selenium_script.pages.login_page import LoginPage

from src.selenium_script.exceptions.homepage import LoginRedirectFailed
from src.selenium_script.exceptions.login_page import LoginPageElementNotFound, LoginProcedureFailed, LoginVerificationError

from src.selenium_script.utils.cookies import load_cookies,save_cookies
def perform_login(driver : ChromeWebdriver) -> tuple[bool,str|Exception]:
    home = HomePage(driver)
    if not home.is_home_page():
        return False , NoSuchElementException("Missing home page elements.")
    
    #go to login url
    # XXX edit the logic here later #
    load_cookies(driver)
    # if cookies loaded properly and we try to go to login page logout will be present.
    try:
        home.go_to_login_page()
    except LoginRedirectFailed as e:
        return False , e
    
    login_page = LoginPage(driver)
    try:
        login_page.is_login_page()
    except LoginPageElementNotFound as e:
        return False, e
    #short circuit if the check works#
    if login_page.valid_login():
        return True, ''
    #else it'll go about its pathway
    try:
        login_page.perform_login(config.ACCOUNTS[0],config.PASSWORD)
    except LoginProcedureFailed as e:
        return False , e
    
    try:
        login_page.valid_login()
    except LoginVerificationError as e:
        return False, e
    
    return True,''
