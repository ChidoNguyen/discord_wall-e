import os
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navigate_download_history(bot_webdriver):
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

def check_download_limit(bot_webdriver):
    try:
        out_of_ten = bot_webdriver.find_element(By.CSS_SELECTOR , 'div.m-v-auto.d-count')
    except NoSuchElementException as e:
        print(e)
    str_limit = out_of_ten.text
    if str_limit == "10/10":
        return True
    return False

def max_limit(bot_webdriver):
    homepage_url = bot_webdriver.current_url
    down_limit = check_download_limit(navigate_download_history(bot_webdriver))
    bot_webdriver.get(homepage_url)
    return down_limit

'''
Util Function - Output_Template to modify search results
Args : User folder for file access , list of url links
'''
def output_template(bot_webdriver,user_folder,links):
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