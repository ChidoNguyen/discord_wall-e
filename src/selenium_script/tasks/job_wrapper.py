from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from src.selenium_script.tasks.jobs.search_job import SearchJob
from src.selenium_script.tasks.jobs.result_job import result_job
from src.selenium_script.tasks.jobs.acquire_job import acquire_job
from src.selenium_script.exceptions.script_jobs import SearchJobError,ResultJobError, AcquireJobError
from src.selenium_script.exceptions.search_results import SearchResultPageError
from src.selenium_script.exceptions.result_detail import ResultDetailJobError
"""
Notes to self:
3 things to handle here Full script and Two 1/2 scripts
1 -> full Search -> Result -> Acquire
2 -> Search - > Result /end
3 -> <...> /start Acquire 
"""



def _get_handle(driver : ChromeWebdriver, search_query: str):
    """
    Main script job gets top/first search result

    Chains together Search -> Results -> Acquire jobs
    """
    # start the search
    search_job = SearchJob(driver,search_query)
    try:
        search_job.perform_search()
    except SearchJobError as e:
        return e
    
    # generate result info
    try:
        result_urls = result_job(driver)
    except ResultJobError as e:
        return e
    
    # acquire 
    try:
        acquire_job()
    pass

def _get_advance_handle():
    pass
def _pick_handle():
    pass

def perform_script_option(*,driver: ChromeWebdriver, download_dir: str, option: str):
    """
    Entry point for core jobs of script. Will delegate and invoke the proper job to function correlation.
    """

    #don't think we need to add arg. checker script itself is pretty atomic won't work up to this point... but we'll see

    option_handler_map = {
        'getbook' : _get_handle,
        'getbook-adv' : _get_advance_handle,
        'pick' : _pick_handle
    }
    
    temp_holder = option_handler_map[option]()
    pass