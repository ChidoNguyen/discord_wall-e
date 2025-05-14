import os
import sys
from dotenv import load_dotenv
###
load_dotenv(dotenv_path=".env.automation")
pythonpath = os.getenv('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0,pythonpath)
###
class ScriptConfig:
    REQUIRED_VARS = [
        "URL", "ACCOUNTS", "PASS"
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
config_automation = ScriptConfig()