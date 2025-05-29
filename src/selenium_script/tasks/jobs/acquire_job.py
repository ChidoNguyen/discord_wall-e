from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebdriver

#utils
from src.selenium_script.utils.downloads import get_folder_snapshot , check_download_status , rename_download

#exceptions
from src.selenium_script.pages.results_details_page import ResultDetailPage
from src.selenium_script.exceptions.result_detail import ResultDetailJobError

def _get_details_page(*,driver: ChromeWebdriver, url: str):
    """
    Create details_page ui handler object.
    """
    details_page = ResultDetailPage(driver)
    details_page.load(details_url=url)

    if url not in driver.current_url:
        raise ResultDetailJobError(
            message="Did not load details page properly."
        )
    return details_page


def acquire_job(*,driver : ChromeWebdriver , download_dir: str, details_url: str) -> dict[str,str]:
    details_page = _get_details_page(driver=driver,url = details_url)
    
    old_files = get_folder_snapshot(user_folder=download_dir,key="path")
    details_page.download()

    check_download_status(user_folder=download_dir,old_files=old_files)
    return rename_download(download_path=download_dir)
