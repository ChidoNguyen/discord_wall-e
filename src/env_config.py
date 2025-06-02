import os
import sys
from dotenv import load_dotenv

#load .env file
load_dotenv()

#include src for import resolution
pythonpath = os.getenv('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0,pythonpath)
class Config:
    '''
    Loads .env file and variables into one class
    '''
    #### Type Hinting/Autocomplete Assist ###
    DISCORD_TOKEN: str
    ADMIN_ID: str | int
    JANITORS: str | int
    PERSONAL_TEST: str | int | None = None
    DOWNLOAD_DIR: str
    DB_PATH: str 
    THE_VAULT: str 
    THE_JOBS: str
    API_ENDPOINT: str 
    THE_GOODS: str
    CACHE_FOLDER: str
    #########################################
    REQUIRED_ENV_VARS = [
        'DISCORD_TOKEN', 'ADMIN_ID', 'JANITORS', 'PERSONAL_TEST',
        'DOWNLOAD_DIR', 'DB_PATH', 'THE_VAULT', 'THE_JOBS',
        'API_ENDPOINT', 'THE_GOODS', 'CACHE_FOLDER'
    ]
    #pretty much any ID related discord stuff
    REQUIRED_INT_VARS = [
        'ADMIN_ID', 'JANITORS', 'PERSONAL_TEST'
    ]
    def __init__(self):
        missing_env_vars = []
        for var in self.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value is None:
                missing_env_vars.append(var)
            else:
                if var in self.REQUIRED_INT_VARS:
                    try:
                        value= int(value)
                    except ValueError:
                        raise RuntimeError(f'Env variable {var} must be an integer.')
                setattr(self,var,value)

        # Warning for missing vars
        if missing_env_vars:
            raise RuntimeError(f"Missing required env variables : {', '.join(missing_env_vars)}")
        


config = Config()
