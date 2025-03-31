import os
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from ebooklib import epub

def _navigate_download_history(bot_webdriver):
    """
    Function : Navigate to our target sites download history
    
    Arguments : webdriver

    Returns : webdriver or None
    """

    LIMIT_XPATH = {
        "download_history" : "//a[@href='/users/downloads']"
    }
    try:
        click_link = bot_webdriver.find_element(By.XPATH , LIMIT_XPATH["download_history"])
        href_link = click_link.get_attribute('href')
    except NoSuchElementException as e:
        print(e)
    try:
        bot_webdriver.get(href_link)
    except:
        print("Download history failed to follow URL.")
    return bot_webdriver

def _check_download_limit(bot_webdriver):
    """
    Function : Checks to see if we have hit download limit
    
    Arguments : webdriver

    Returns : bool
    """
    try:
        out_of_ten = bot_webdriver.find_element(By.CSS_SELECTOR , 'div.m-v-auto.d-count')
    except NoSuchElementException as e:
        print(e)
    str_limit = out_of_ten.text
    if str_limit == "10/10":
        return True
    return False

def _check_max_limit(bot_webdriver):
    """
    Function : Wrapper function to navigate and check download limit
    
    Arguments : webdriver

    Returns : bool
    """
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
            print(f"prolly failed cause we're too fast {e}")
        json_object = {
            'link' : url,
            'author' : author,
            'title' : title
        }
        json_data.append(json_object)
    
    with open(os.path.join(user_folder,'results.json'),'w') as json_file:
        json.dump(json_data,json_file,indent=4)

def _get_download_metadata(target_file : str):
    """
    Function : extracts metadata for epub files
    
    Arguments : target_file - str - full path to file

    Returns : dictionary with keys author/title and value associated to them
    """
    literature = epub.read_epub(target_file)
    lit_author = literature.get_metadata('DC','creator')[0][0]
    lit_title = literature.get_metadata('DC','title')[0][0]
    
    return { 'author' : lit_author , 'title' : lit_title }