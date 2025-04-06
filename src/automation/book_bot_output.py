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
                'status' : 'initialized',
                'metadata' : None,
                'steps' : [],
                'misc' : []
            }
        return cls._instance
    
    def bot_updates(self,key,data):
        match key:
            case 'status':
                self.output[key] = data
            case 'metadata':
                self.output[key] = data
            case 'steps':
                self.output[key].append(data)
            case _:
                self.output['misc'].append(data)

    def get_output(self):
        return self.output
    
    def get_json_output(self):
        return json.dumps(self.output)

book_bot_status = BookScriptStatus()