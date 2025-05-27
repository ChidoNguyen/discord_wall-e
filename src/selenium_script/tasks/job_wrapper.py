from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from src.selenium_script.tasks.jobs.search_job import SearchJob
from src.selenium_script.tasks.jobs.result_job import result_job
from src.selenium_script.tasks.jobs.acquire_job import acquire_job
from src.selenium_script.tasks.jobs.pick_job import create_options_job, save_options_json
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
def _get_handle(driver : ChromeWebdriver, search_query: str , download_dir: str):
    """
    Main script job gets top/first search result

    Chains together Search -> Results -> Acquire jobs
    """
    # start the search
    search_job = SearchJob(driver,search_query)
    try:
        search_job.perform_search()
    except SearchJobError as e:
        raise 
    
    # generate result info
    try:
        result_urls = result_job(driver)
    except ResultJobError as e:
        raise
    
    # acquire 
    try:
        acquire_status = acquire_job(driver=driver, download_dir=download_dir,results=result_urls)
    except Exception as e:
        raise
    
    if acquire_status:
        print(acquire_status)

def _get_advance_handle(driver : ChromeWebdriver , search_query: str, download_dir:str):
    ''' Short circuits after search job , no need to acquire '''
    search_job = SearchJob(driver,search_query)
    try:
        search_job.perform_search()
    except SearchJobError as e:
        raise 
    
    # generate result info
    try:
        result_urls = result_job(driver)
    except ResultJobError as e:
        raise

    #### Need to output results ####
    try:
        options = create_options_job(driver=driver,results=result_urls)
    except:
        raise
    
    try:
        save_options_json(processed_results=options,download_dir=download_dir)
    except:
        raise
    
    return True

def _pick_handle():
    ''' Entry at acquire , doesnt run the first 2 jobs '''
    pass

def perform_script_option(*,driver: ChromeWebdriver, download_dir: str, search: str, option: str):
    """
    Entry point for core jobs of script. Will delegate and invoke the proper job to function correlation.
    """
    #don't think we need to add arg. checker script itself is pretty atomic won't work up to this point... but we'll see

    option_handler_map = {
        'getbook' : _get_handle,
        'getbook-adv' : _get_advance_handle,
        'pick' : _pick_handle
    }
    
    try:
        option_handler_map[option](driver,search,download_dir)
    except Exception as e:
        return False , e 
    return True , None