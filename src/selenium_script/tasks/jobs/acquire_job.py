from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement

from src.selenium_script.script_config import config_automation as config

from src.selenium_script.pages.results_details_page import ResultDetailPage
from src.selenium_script.exceptions.result_detail import ResultDetailJobError , ResultDetailPageError

def acquire_job(driver: ChromeWebdriver, results: list[str], url_idx : int = 0):
    # should fully have a file at the end of script 
    detail_url_idx = results[url_idx]
    details_page = ResultDetailPage(driver,detail_url_idx)
    return 
    