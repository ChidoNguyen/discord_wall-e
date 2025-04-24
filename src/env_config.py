import os

from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
JANITORS = os.getenv('JANITORS')
PERSONAL_TEST = os.getenv('PERSONAL_TEST')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
DB_PATH = os.getenv('DB_PATH')
THE_VAULT = os.getenv('THE_VAULT')
THE_JOBS = os.getenv('THE_JOBS')
