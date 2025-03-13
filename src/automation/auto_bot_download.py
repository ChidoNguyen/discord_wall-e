from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException , TimeoutException
import os, time, re

#rawest form of "download"
def rename_book_file(book,author,user_folder):
    try:
        book = re.sub(r'[<>:"/\\|?*]', '', book) #replaces special chars with spaces
        all_files = [os.path.join(user_folder, files) for files in os.listdir(user_folder)]
        if not all_files:
            raise OSError("Empty directory")
        newest = max(all_files, key = os.path.getctime)
        os.rename(newest,os.path.join(user_folder, f'{book} by {author}.epub'))
    except Exception as e:
        print(f'Error failed to rename file. {e}')
        return False 
    return True

def download_progress(user_folder, timeout_limit = 60):
    download_complete = False
    time.sleep(5)
    timeout_counter = 0
    #timeout_limit = 60
    while not download_complete and timeout_counter < timeout_limit:
        download_complete = True
        for file_names in os.listdir(user_folder):
            if file_names.endswith('.crdownload'):
                download_complete = False
        timeout_counter += 1
        time.sleep(1)
    
    return download_complete

def download_attempt(bot_webdriver, link_url, user_folder):
    #we need the driver and the url

    bot_webdriver.get(link_url) 
    #find the download button

    try:
        wait = WebDriverWait(bot_webdriver, 10)
        dl_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-default.addDownloadedBook")))
        dl_button.click()
    except NoSuchElementException as e:
        print(f'Error clicking the download link and button. {e}')
        return None
    except TimeoutException as e:
        print(f'Timeout error trying to locate download button. {e}')
        return None

    #extract authoer title for file renaming
    '''
    try:
        book_name = bot_webdriver.find_element(By.XPATH, '//h1[@itemprop= "name"]').text
        author_name = bot_webdriver.find_element(By.XPATH, '//a[@class= "color1"][@title="Find all the author\'s book"]').text
    except NoSuchElementException as e:
        print(f'Error in extracting book name and author name. {e}')
        return None
    '''
    book_name = ""
    author_name = ""
    #download complete check

    if download_progress(user_folder):
        if rename_book_file(book_name,author_name,user_folder):
            return bot_webdriver
    return None

def start_download(bot_webdriver,user_folder,url):
    return download_attempt(bot_webdriver,url,user_folder)
    
