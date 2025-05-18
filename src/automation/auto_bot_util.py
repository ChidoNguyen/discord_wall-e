import os
import json
import re

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , NoSuchAttributeException

from ebooklib import epub
import warnings

from src.automation.book_bot_output import book_bot_status

####ebooklib future/user warning ######
warnings.filterwarnings(
    'ignore', 
    message = 'In the future version we will turn default option ignore_ncx to True.', 
    category=UserWarning
    )
warnings.filterwarnings(
    'ignore',
    message=(".*This search incorrectly ignores the root element, and will be fixed in a future version.*"),
    category=FutureWarning
    )
######
def _navigate_download_history(bot_webdriver: ChromeWebDriver) -> ChromeWebDriver | None:
    """
    Function : Navigate to our target sites download history
    
    Arguments : webdriver

    Returns : webdriver or None
    """
    # Dict if we ever need to expand on
    #LIMIT_XPATH = {
    #    "download_history" : "//a[@href='/users/downloads']"
    #}
    

    xpath_download_limit = "//a[@href='/users/downloads']"
    
    try:
        download_history_elem: WebElement = bot_webdriver.find_element(By.XPATH,xpath_download_limit)
        download_history_url = download_history_elem.get_attribute('href')
        if not download_history_url:
            book_bot_status.updates(('Error', "[Error] [DL_History_URL] : No URL found."))
            return None
        bot_webdriver.get(download_history_url)
    except NoSuchElementException as e:
        book_bot_status.updates(('Error', f"[Error] [Navigate Download History] : {e}"))
        return None
    return bot_webdriver

def _check_download_limit(bot_webdriver: ChromeWebDriver) -> bool:
    """
    Function : Checks to see if we have hit download limit
    
    Arguments : webdriver

    Returns : bool
    """
    css_out_of_ten = 'div.m-v-auto.d-count'
    target_out_of_ten_text = "10/10"
    try:
        out_of_ten_elem = bot_webdriver.find_element(By.CSS_SELECTOR , css_out_of_ten)
        if out_of_ten_elem.text.strip() == target_out_of_ten_text:
            return True
    except NoSuchElementException as e:
        book_bot_status.updates(('Error',f'Error - Missing Download Limit Element {e}'))  
    return False

def _check_max_limit(bot_webdriver: ChromeWebDriver) -> bool:
    """
    Function : Wrapper function to navigate and check download limit
    
    Arguments : webdriver

    Returns : bool
    """
    #saved to go back to#
    homepage_url = bot_webdriver.current_url
    

    down_limit = _check_download_limit(_navigate_download_history(bot_webdriver))
    bot_webdriver.get(homepage_url)
    return down_limit


def _output_template(bot_webdriver,user_folder,links):
    """
    Function : formats our results from search into json
    
    Arguments : 
        bot_webdriver : webdriver
        user_folder : str - full path to where downloading/saving occurs
        links - List(str) - a list of strings 

    Returns : -
    """
    #need to build json-object
    json_data = []
    for url in links:
        #access each link grab author / title info 
        bot_webdriver.get(url)
        title , author = None , None
        try:
            title = bot_webdriver.find_element(By.XPATH, '//h1[@itemprop= "name"]').text
            author = bot_webdriver.find_element(By.XPATH, '//a[@class= "color1"][@title="Find all the author\'s book"]').text
        except Exception as e:
            book_bot_status.updates(('Error',f'Error - Output Title/Author Extraction {e}'))
            #print(f"prolly failed cause we're too fast {e}")
        json_object = {
            'link' : url,
            'author' : author,
            'title' : title
        }
        json_data.append(json_object)
    
    with open(os.path.join(user_folder,'results.json'),'w') as json_file:
        json.dump(json_data,json_file,indent=4)
    return True

def _get_download_metadata(target_file : str):
    """
    Function : extracts metadata for epub files
    
    Arguments : target_file - str - full path to file

    Returns : dictionary with keys author/title and value associated to them
    """
    literature = epub.read_epub(target_file)
    lit_author = literature.get_metadata('DC','creator')[0][0]
    lit_title = literature.get_metadata('DC','title')[0][0]
    #sanitize
    lit_author = re.sub(r'[<>:"/\\|?*]', '', lit_author)
    lit_title = re.sub(r'[<>:"/\\|?*]', '', lit_title)
    #lit author clean up
    lit_author = ' '.join(lit_author.strip().split())
    fname , lname = '' , ''

    #for lname, fname formatting
    if ',' in lit_author: 
        name_parse = [n.strip() for n in lit_author.split(',',1)]
        lname = name_parse[0]
        if len(name_parse) > 1:
            fname = name_parse[1]
    else:
        name_parse = lit_author.split()
        if len(name_parse) == 1:
            lname = name_parse[0]
        else:
            lname = name_parse[-1]
            fname = ' '.join(name_parse[:-1])
            #fname = name_parse[0]
            #lname = ' '.join(name_parse[1:])

    
    return {'fname' : fname, 'lname' : lname, 'title' : lit_title } 