import os
from dotenv import load_dotenv
###
load_dotenv(dotenv_path= os.path.join(os.path.dirname(__file__),".env.automation"))
###
class ScriptConfig:
    URL : str
    ACCOUNTS: str | list[str]
    PASSWORD: str
    TARGET_TITLE: str
    COOKIES_DIR: str
    REQUIRED_VARS = [
        "URL", "ACCOUNTS", "PASSWORD","TARGET_TITLE","COOKIES_DIR"
    ]
    def __init__(self):
        missing_var = []
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if value is None:
                missing_var.append(var)
            setattr(self,var,value)
        if missing_var:
            raise RuntimeError(f"[WARNING] Missing env.automation variables - {', '.join(missing_var)}")
        ##process accounts
        self._convert_accounts_raw_string()
        self._create_cookies_dir()
        
    def _convert_accounts_raw_string(self):
        if self.ACCOUNTS is not None and isinstance(self.ACCOUNTS,str):
            self.ACCOUNTS = [ user.strip() for user in self.ACCOUNTS.split(',') if user.strip()]

    def _create_cookies_dir(self):
        if not os.path.exists(self.COOKIES_DIR):
            os.makedirs(self.COOKIES_DIR)

config_automation = ScriptConfig()
