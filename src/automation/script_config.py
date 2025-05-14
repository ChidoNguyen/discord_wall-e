import os
import sys
from typing import Optional
from dotenv import load_dotenv
###
load_dotenv(dotenv_path= os.path.join(os.path.dirname(__file__),".env.automation"))

class ScriptConfig:
    URL : Optional[str] = None
    ACCOUNTS: Optional[list[str]] = None
    PASSWORD: Optional[str] = None
    TARGET_TITLE: Optional[str] = None
    REQUIRED_VARS = [
        "URL", "ACCOUNTS", "PASSWORD","TARGET_TITLE"
    ]
    def __init__(self):
        missing_var = []
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if value is None:
                missing_var.append(var)
            setattr(self,var,value)
        if missing_var:
            print(f"[WARNING] Missing env.automation variables - {', '.join(missing_var)}")
        ##process accounts
        self.ACCOUNTS = [ user.strip() for user in self.ACCOUNTS.split(',') if user.strip()]
config_automation = ScriptConfig()