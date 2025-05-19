from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from pages.homepage import HomePage
from pages.login_page import LoginPage
def perform_login(driver : ChromeWebdriver):
    home = HomePage(driver)
    if not home.is_home_page():
        return False , "Not on home page"
    
    navigation_status , error_msg = home.go_to_login_page()
    if not navigation_status:
        return False , "Webdriver could not get to login url."
    login_page = LoginPage(driver)
    if not login_page.is_login_page():
        return False , "Might not be on login page"
    
    try:
        login_page.perform_login(config.ACCOUNTS[0],config.PASSWORD)
    except Exception as e:
        return False , str(e)
    
    if not login_page.valid_login():
        return False
    
    return True
