from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.remote.webelement import WebElement

from src.selenium_script.script_config import config_automation as config

from src.selenium_script.pages.results_details_page import ResultDetailPage
from src.selenium_script.exceptions.result_detail import ResultDetailJobError , ResultDetailPageError

def acquire_job(driver: ChromeWebdriver, results: list[str], url_idx : int = 0):
    # should fully have a file at the end of script

    # Default idx is 0 for "top"/"first" result
    # if in "pick" mode we pass in index as needed

    detail_url = results[url_idx]

    details_page = ResultDetailPage(driver,detail_url)
    details_page.load()
    # check 
    if detail_url not in driver.current_url:
        raise ResultDetailJobError(
            message="Did not load details page properly."
        )
    
    #start the d.l.
    try:
        details_page.download()
    except ResultDetailPageError as e:
        raise e
    
    return 

#load up our details page handler

# grab the download "starter"

# initiate the download
    