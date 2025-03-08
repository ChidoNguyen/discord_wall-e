from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
