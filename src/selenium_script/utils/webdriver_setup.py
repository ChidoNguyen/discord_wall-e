import platform

from selenium.webdriver.chrome.webdriver import  WebDriver as ChromeWebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions

from src.selenium_script.utils.script_status import book_bot_status
from src.selenium_script.utils.util import create_user_save_dir

def _build_chrome_options(download_path: str, headless: bool = True) -> ChromeOptions:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    
    ### define what options we want loaded ###
    chrome_args = [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1200,800",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-default-apps",
        "--disable-translate",
        "--disable-popup-blocking",
        "--metrics-recording-only",
        "--disable-hang-monitor",
        "--safebrowsing-disable-auto-update",
        "--disable-blink-features=AutomationControlled"
    ]
    for arg in chrome_args:
        options.add_argument(arg)
    
    ### driver preferences ###
    prefs = {
        "download.default_directory" : download_path ,
        "savefile.default_directory" : download_path , 
        "download.prompt_for_download" : False ,
        "directory_upgrade" : True,
        "profile.managed_default_content_settings.images": 2 #new
    }
    options.add_experimental_option('prefs',prefs)
    
    return options

def _create_chrome_driver(chrome_options: ChromeOptions) -> ChromeWebDriver:
    ''' creates webdriver instance '''
    return ChromeWebDriver(options=chrome_options,service=Service('/usr/bin/chromedriver')) if platform.system() == 'Linux' else ChromeWebDriver(options=chrome_options)
    
def setup_webdriver(user: str, headless: bool = True) -> ChromeWebDriver | None:
    """
    Initializes our chrome webdriver

    Arguments:
        user(str): Will be used to name download directory
    """

    try:
        download_path = create_user_save_dir(user)
    except Exception as e:
        book_bot_status.updates(("Error" , f"[Error] [Setup - Download path] : {e}"))
        return None
    
    options=_build_chrome_options(download_path,headless=headless)

    return _create_chrome_driver(options)
