import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        try:
            self.DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
            self.ADMIN_ID = int(os.getenv('ADMIN_ID'))
            self.JANITORS = int(os.getenv('JANITORS'))
            self.PERSONAL_TEST = int(os.getenv('PERSONAL_TEST'))
            self.DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
            self.DB_PATH = os.getenv('DB_PATH')
            self.THE_VAULT = os.getenv('THE_VAULT')
            self.THE_JOBS = os.getenv('THE_JOBS')
            self.API_ENDPOINT = os.getenv('API_ENDPOINT')
            self.THE_GOODS = os.getenv('THE_GOODS')
        except Exception as e:
            print(e)

config = Config()
