import os
import time
import json

COOKIES = {
    'path' : "cookies",
    'fname' : 'bot_cookies.json'
}

'''
epoch : true if not expired // other wise false 
'''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR,COOKIES['path'])

#open with 'w' only creates files not dir, self manage
if not os.path.exists(COOKIES_PATH):
    os.makedirs(COOKIES_PATH)

def _valid_cookies():
    cookies_json = None
    try:
        with open(os.path.join(COOKIES_PATH,COOKIES['fname']), 'r') as file:
            cookies_json = json.load(file)
    except Exception as e:
        print(f'Error : no current cookies on file, will attempt to create.')
        return False
    
    for components in cookies_json[1:]:
        if 'expiry' in components and int(components['expiry']) <= int(time.time()):
            return False
    return True

def _load_cookies(bot_webdriver):
    cookies_json = None
    try:
        with open(os.path.join(COOKIES_PATH, COOKIES['fname']), 'r') as file:
            cookies_json = json.load(file)
    except Exception as e:
        print(f'Error: {e}')
        return False
    
    try:
        for cookie in cookies_json:
            if 'expiry' in cookie and isinstance(cookie['expiry'] , float):
                cookie['expiry'] = int(cookie['expiry'])
            bot_webdriver.add_cookie(cookie)
    except Exception as e:
        print(f'Error: {e}')
        return False
    
    try:
        bot_webdriver.refresh()
        return True
    except Exception as e:
        print(f'Cookies failed to load. Error : {e}')
        return False

def _save_cookies(bot_webdriver):
    cookies = bot_webdriver.get_cookies()
    try:
        with open(os.path.join(COOKIES_PATH, COOKIES['fname']), 'w') as file:
            json.dump(cookies,file)
    except Exception as e:
        print(f'Cookies failed to save. Error : {e}')
        return False
if __name__ == '__main__':
    print(COOKIES_PATH)