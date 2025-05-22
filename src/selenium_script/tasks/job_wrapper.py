from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

"""
Notes to self:
3 things to handle here Full script and Two 1/2 scripts
1 -> full Search -> Result -> Acquire
2 -> Search - > Result /end
3 -> <...> /start Acquire 
"""

def perform_script_option():
    """
    Entry point for core jobs of script. Will delegate and invoke the proper job to function correlation.
    """
    pass