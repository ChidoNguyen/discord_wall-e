import configparser
import os
#cleaning up the config/env stuff
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # dir of where this file is
CONFIG_PATH = os.path.join(BASE_DIR,"book_bot_config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
download_dir = config.get("USER" , "download_dir")
url = config.get("WEB" , "url")
userID = config.get("WEB" , "userID")
userPass = config.get("WEB" , "userPass")