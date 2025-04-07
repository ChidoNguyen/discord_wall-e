from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException , TimeoutException
import os
import time
import shutil

from src.automation.auto_bot_util import _get_download_metadata
from src.automation.book_bot_output import book_bot_status

def _rename_book_file(user_folder):
    """
    Function : Renames a book file
    
    Arguments : 
        user_folder : str - full path to where we want to save our file

    Returns : True if successful / False if an error occured during the process
    """
    try:

        all_files = [os.path.join(user_folder, files) for files in os.listdir(user_folder)]
        if not all_files:
            raise OSError("Empty directory")
        newest = max(all_files, key = os.path.getctime)
        metadata = _get_download_metadata(newest)
        new_title = f'{metadata["title"]} by {metadata["author"]}.epub'
        #os.rename(newest, os.path.join(user_folder,new_title))
        newname_file_path = shutil.move(newest,os.path.join(user_folder,new_title)) # acts the same in windows and linux env. vs os.rename
        head , username = os.path.split(user_folder)

        #### Update our global output #####
        file_info = {
            'source' : f'{newname_file_path}.finish',
            'title' : metadata['title'],
            'author' : metadata['author'],
            'username' : username
        }
        book_bot_status.updates(('metadata',file_info))
    except Exception as e:
        book_bot_status.updates(('Error','Error - failed file rename'))
        #print(f'Error failed to rename file. {e}')
        return False 
    return True


def _check_download_progress(user_folder, timeout_limit = 60):
    """
    Function : Checks for when file download is completed
    
    Arguments : 
        user_folder : str - path to file save location
        timeout_limit : int = defaults to 60 sec expected downloads max time 

    Returns : Bool
    """
    download_complete = False
    time.sleep(5)
    timeout_counter = 0
    while not download_complete and timeout_counter < timeout_limit:
        download_complete = True
        for file_names in os.listdir(user_folder):
            if file_names.endswith('.crdownload'):
                download_complete = False
        timeout_counter += 1
        time.sleep(1)
    
    return download_complete

def _download_attempt(bot_webdriver, link_url, user_folder):
    """
    Function : Initiates the file download attempt
    
    Arguments : 
        bot_webdriver : selenium webdriver element
        link_url : str - webpage of where our download link is located
        user_folder : str - full path where to save to 

    Returns : 
        webdriver - if successful 
        None    - if fail
    """
    bot_webdriver.get(link_url) 
    try:
        wait = WebDriverWait(bot_webdriver, 10)
        dl_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-default.addDownloadedBook")))
        dl_button.click()
    except NoSuchElementException as e:
        book_bot_status.updates(('Error',f'Error - Missing download elements {e}'))
        #print(f'Error clicking the download link and button. {e}')
        return None
    except TimeoutException as e:
        book_bot_status.updates(('Error',f'Error - Timeout error on download button {e}'))
        #print(f'Timeout error trying to locate download button. {e}')
        return None

    #download complete check

    if _check_download_progress(user_folder):
        if _rename_book_file(user_folder):
            return bot_webdriver
    return None

def start_download(bot_webdriver,user_folder,url):
    """
    Function : Wrapper function to start the full download process
    
    Arguments : webdriver , path to save file , site url

    Returns : the webdriver or None
    """
    return _download_attempt(bot_webdriver,url,user_folder)
    
