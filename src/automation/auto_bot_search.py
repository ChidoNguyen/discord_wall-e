from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .book_bot_config import url as site_url
from src.automation.book_bot_output import book_bot_status

MAX_RESULTS = 10
XPATH = {
        's_field' : "//input[@id= 'searchFieldx']",
        's_button' : "//button[@type= 'submit' and @aria-label='Search']"
    }
def _search_query_input(bot_webdriver, search_query):
    """
    Function : Automates the input of our search string into search input field
    
    Arguments : 
        bot_webdriver : selenium webdriver 
        search_query : str - what we're searching for  

    Returns : webdriver or None
    """
    try:
        search_field = bot_webdriver.find_element(By.XPATH, XPATH['s_field'])
    except NoSuchElementException as e:
        book_bot_status.updates(('Error',f'Error - Search Field Element {e}'))
        #print(f'Error: {e}')
        return None
    
    try:
        search_field.send_keys(search_query)
        search_button = bot_webdriver.find_element(By.XPATH, XPATH['s_button']).click()
    except NoSuchElementException as e:
        book_bot_status.updates(('Error',f'Error - Search Field Input {e}'))
        #print(f'Error: {e}')
        return None
    
    return bot_webdriver

def _get_search_result(bot_webdriver):
    """
    Function : Extracts our search results max results set via global variable
    
    Arguments :
        bot_webdriver : selenium webdriver

    Returns : tuple(webdriver,list) or None
        webdriver - selenium webdriver
        List[str] - search results
    """
    book_deets = {
        'book_card' : 'z-bookcard',

    }
    search_results= bot_webdriver.find_elements(By.CLASS_NAME, "book-item") #grab all search results
    #truncate our results to 10 results max
    #if len(search_results) > MAX_RESULTS:
     #   search_results = search_results[:MAX_RESULTS]
    valid_links = []
    try:
        for items in search_results:
            book_details = items.find_element(By.TAG_NAME, book_deets['book_card'])
            bd_lang = book_details.get_attribute('language').lower()
            bd_extension = book_details.get_attribute('extension').lower()
            if bd_lang == 'english' and bd_extension == 'epub' :
                full_link_path = site_url + book_details.get_attribute('href')[1:] # removing starting / from href
                valid_links.append(full_link_path)
    except Exception as e:
        book_bot_status.updates(('Error',f'Error - Link Extraction {e}'))
        #print(f'Error: {e} \nBook search link extraction failed.')
        return None
    
    return bot_webdriver , valid_links[:MAX_RESULTS]


def bot_search(bot_webdriver, search_query):
    """
    Function : Wrapper function for search process
    
    Arguments :
        bot_webdriver : - selenium webdriver
        search_query: str - what we want to look up

    Returns : tuple(webdriver,List(str)) or None
    """
    search_outcome = _search_query_input(bot_webdriver,search_query)
    return _get_search_result(search_outcome)
   