from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.selenium_script.script_config import config_automation as config

from src.selenium_script.tasks.jobs.search_job import SearchJob
from src.selenium_script.tasks.jobs.result_job import result_job
from src.selenium_script.tasks.jobs.acquire_job import acquire_job
from src.selenium_script.tasks.jobs.option_job import create_options_job, save_options_json
from src.selenium_script.exceptions.script_jobs import ScriptJobRunnerError, SearchJobError,ResultJobError, AcquireJobError
from src.selenium_script.exceptions.search_results import SearchResultPageError , NoSearchResultsError
from src.selenium_script.exceptions.result_detail import ResultDetailJobError
"""
Notes to self:
3 things to handle here Full script and Two 1/2 scripts
1 -> full Search -> Result -> Acquire
2 -> Search - > Result /end
3 -> <...> /start Acquire 
"""
def _is_empty(data: list[str]):
    if data is None:
        raise NoSearchResultsError(
            message="Empty list of results url.",
            action="job_wrapper -> post search results processing"
        )
    return
def _get_handle(driver: ChromeWebdriver, search_query: str, download_dir: str):
    """
    Executes the advanced search job pipeline: performs a search, processes results, and saves output to disk.

    Args:
        driver (ChromeWebdriver): Active Selenium driver instance.
        search_query (str): Search query string to perform.
        download_dir (str): Path to directory where output will be saved.

    Raises:
        SearchJobError: If the search task fails to execute.
        ResultJobError: If result job tasks fails to execute.
        Result
    """
    search_job = SearchJob(driver,search_query)
    search_job.perform_search()
    result_urls = result_job(driver)
    _is_empty(result_urls) # guard to trigger an exception
    #takes "top" result
    get_url = result_urls[0]
    file_metadata = acquire_job(driver=driver,download_dir=download_dir,details_url=get_url)
    return file_metadata

def _get_advance_handle(driver: ChromeWebdriver, search_query: str, download_dir: str):
    """
    Executes the advanced search job pipeline: performs a search, processes results, and saves output to disk.

    Args:
        driver (ChromeWebdriver): Active Selenium driver instance.
        search_query (str): Search query string to perform.
        download_dir (str): Path to directory where output will be saved.

    Raises:
        SearchJobError: If the search task fails to execute.
        ResultDetailJobError: If extracting results from the search page fails.
        ResultDetailPageError: If selenium related interactions are failing.
        SearchResultPageError: If validation of search results fails.
        ChoiceCreationJobError: If options results are empty or could not be saved to file.
    """
    # search doesn't really have its own "page" since the search bar is live pretty much everywhere , just make a class wrapper for its role.

    search_job = SearchJob(driver,search_query)
    search_job.perform_search()
    result_urls = result_job(driver)
    _is_empty(result_urls)
    options = create_options_job(driver=driver, results=result_urls)
    save_options_json(processed_results=options,download_dir=download_dir)
    return

def _pick_handle(driver: ChromeWebdriver, details_url: str, download_dir: str):
    ''' Entry at acquire , doesnt run the first 2 jobs '''
    #big difference here is that search_query is actually the url directly to the details page
    #skips the need to search and results straight to acquire
    file_metadata = acquire_job(driver=driver,download_dir=download_dir,details_url=details_url)
    return file_metadata

def perform_script_option(*,driver: ChromeWebdriver, download_dir: str, search: str, option: str) -> tuple[bool, Exception | dict | None]:
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
        job_status = option_handler_map[option](driver,search,download_dir)
    except Exception as e:
        return False,e 
    return True , job_status