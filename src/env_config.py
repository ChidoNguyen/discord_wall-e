import os
import sys
from typing import Optional
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
    DISCORD_TOKEN: Optional[str] = None
    ADMIN_ID: Optional[str] = None
    JANITORS: Optional[str] = None
    PERSONAL_TEST: Optional[str] = None
    DOWNLOAD_DIR: Optional[str] = None
    DB_PATH: Optional[str] = None
    THE_VAULT: Optional[str] = None
    THE_JOBS: Optional[str] = None
    API_ENDPOINT: Optional[str] = None
    THE_GOODS: Optional[str] = None
    #########################################
    REQUIRED_ENV_VARS = [
        'DISCORD_TOKEN', 'ADMIN_ID', 'JANITORS', 'PERSONAL_TEST',
        'DOWNLOAD_DIR', 'DB_PATH', 'THE_VAULT', 'THE_JOBS',
        'API_ENDPOINT', 'THE_GOODS'
    ]
    #pretty much any ID related discord stuff
    REQUIRED_INT_VARS = [
        'ADMIN_ID', 'JANITORS', 'PERSONAL_TEST'
    ]
    def __init__(self):
        missing_env_vars = []
        missing_int_vars = []
        for var in self.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if value is None:
                missing_env_vars.append(var)
            setattr(self,var,value)

        # Warning for missing vars
        if missing_env_vars:
            print(f"[WARNING] Missing .env variables: {', '.join(missing_env_vars)}")

        # Int type check/conversion
        for var in self.REQUIRED_INT_VARS:
            value = getattr(self,var,None)
            try:
                setattr(self,var,int(value))
            except (TypeError,ValueError):
                missing_int_vars.append(var)
        
        if missing_int_vars:
            print(f"[WARNING] Failed to convert var to int: {', '.join(missing_int_vars)}")


config = Config()
