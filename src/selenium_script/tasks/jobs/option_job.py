from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver

#utils
from src.selenium_script.utils.util import write_json_file

#page
from src.selenium_script.pages.results_details_page import ResultDetailPage

#exceptions
from src.selenium_script.exceptions.pick_choice import ChoiceCreationJobError


def create_options_job(*,driver: ChromeWebdriver, results: list[str], max_result : int = 10) -> list[dict[str,str]]:
    #instead of acquiring we populate / process a list of results
    """
    Generates list of dictionary items to provide details about each search result option.

    KWargs : 
        driver: Selenium schrome driver for web ui automation
        results: list of url strings correlating to search results
        max_result : pre-set to 10 , to prevent bloat

    Returns : 
        list[dict[str,str]] list of dictionary containing results info 
    """
    
    #technically don't need to check since script is atomic, but in case used elsewhere 
    if not results or max_result <= 0:
        return []
    
    #each entry is an url that redirects to the result'ing items "detail" 

    result_page_handler = ResultDetailPage(driver)
    result_options = []
    for result_url in results[:max_result]:
        result_page_handler.load(details_url=result_url)
        try:
            result_details =result_page_handler.get_results_details()
            result_options.append(result_details)
        except Exception as e:
            raise
    return result_options

def save_options_json(*,processed_results: list[dict[str,str]],download_dir: str):

    if not processed_results:
        raise ChoiceCreationJobError(
            message="Empty list of processed results. No data to output to results json file.",
            action="save_options_json"
        )
    
    try:
        write_json_file(data=processed_results,download_dir=download_dir)
    except (OSError,TypeError) as e:
        raise ChoiceCreationJobError(
            message="Failed to write options to results.json file.",
            action="write_json_file()"
        ) from e

    