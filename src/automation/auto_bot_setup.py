from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import platform , configparser , time , os
from src.automation import bot_site_cookies
from .book_bot_config import download_dir , url , userID , userPass
#prevent config imports for testing
""" print(os.getenv("TEST_MODE"))
if not os.getenv("TEST_MODE"):
    import scripts.bot_site_cookies
    from scripts.book_bot_config import download_dir
else:
    download_dir = None """
#######

#make def. saved folder for user 
def create_user_save_dir(requester):
    user_folder = os.path.join(download_dir, requester)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder

def auto_bot_driver(save_dir):
    #chrome driver options
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless") #no window open during script run
    prefs = {
        "download.default_directory" : save_dir ,
        "savefile.default_directory" : save_dir , 
        "download.prompt_for_download" : False ,
        "directory_upgrade" : True
    }
    options.add_experimental_option('prefs',prefs)
    ###

    bot_driver = None
    if platform.system() == 'Linux': #platform dependent initilization
        service = Service('/usr/bin/chromedriver')
        bot_driver = webdriver.Chrome(service=service , options=options)
    else:
        bot_driver = webdriver.Chrome(options=options)

    return bot_driver

def homepage(bot_driver):
    site_url = url

    bot_driver.get(site_url)
    bot_driver.implicitly_wait(10)
    
    if "Z-Library" in bot_driver.title:
        return bot_driver
    return None

def login_page(bot_driver):
    login_html_text = {
        'login-div' : 'user-data__sign',

    }
    #login page link
    try:
        login_link_div = bot_driver.find_element(By.CLASS_NAME , login_html_text['login-div'])
        anchor_element = login_link_div.find_element(By.TAG_NAME, 'a')
        login_link = anchor_element.get_attribute('href')
        bot_driver.get(login_link) #navigate to login page
        return bot_driver
    except:
        print(f'Failed to identify link for login page.')
        return None

    #login form
def login_creds_input(bot_driver):
    
    uID , uPass = userID , userPass

    login_form = bot_driver.find_element(By.TAG_NAME, "form")
    idEntry = login_form.find_element(By.NAME, 'email').send_keys(uID)
    passEntry = login_form.find_element(By.NAME, 'password').send_keys(uPass)
    submitButton = login_form.find_element(By.TAG_NAME, 'button').click()

    try:
        bot_driver.find_element(By.XPATH, "//a[@href='/logout']")
        return bot_driver
    except:
        print("login attempt failed")
        return None



def auto_bot(requester):
    save_dir = create_user_save_dir(requester)

    ab_driver = auto_bot_driver(save_dir) #setup our initial webdriver client
    homepage_driver = login_element_driver = logged_in_driver = None
    if ab_driver:
        homepage_driver = homepage(ab_driver)

    #cookies check to see if login is needed
    if bot_site_cookies.valid_cookies():
        bot_site_cookies.load_cookies(homepage_driver)
        return homepage_driver, save_dir
    else:
        if homepage_driver:
            login_element_driver = login_page(homepage_driver)
        if login_element_driver:
            logged_in_driver = login_creds_input(login_element_driver)
        bot_site_cookies.save_cookies(logged_in_driver)
        return logged_in_driver, save_dir

if __name__ == '__main__':
    auto_bot("funz")