#singleton approach + global var
import json
class BookScriptStatus:
    _instance = None

    def __new__(cls): #new is the box #init fills it
        #create itself
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.valid_keys = {'status','metadata','steps','misc'}
            cls._instance.output = {
                'status' : 'fail',
                'metadata' : None,
                'steps' : [],
                'message' : None,
                'misc' : []
            }
        return cls._instance
    
    def updates(self,*args):
        for key,data in args:
            match key:
                case 'metadata':
                    self.output[key] = data
                case 'message':
                    self.output[key] = data
                case 'steps':
                    self.output[key].append(data)
                case _:
                    self.output['misc'].append(data)

    def set_status(self,status):
        self.output['status'] = status

    def update_step(self,step:str):
        self.output['steps'].append(step)
        
    def get_output(self):
        return self.output
    
    def get_json_output(self):
        return json.dumps(self.output)

book_bot_status = BookScriptStatus()