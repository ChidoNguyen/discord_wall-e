import json
import time
from dataclasses import dataclass
import os
import shutil
#config
from src.env_config import config
from src.api.models.book_model import UnknownBook , UserDetails
#util

@dataclass
class ScriptServiceExceptionError(Exception):
    message : str
    module: str 
    action : str | None = None
    def __str__(self):
        return (
            f"[{self.module}] {self.message} |"
            f"{f'[Action] {self.action} |' if self.action else ''}"
        )

def build_script_options(*,search_query: UnknownBook , user: UserDetails, option:str ) -> dict[str,str]:
    """
    Builds selenium script required arguments.

    Args:
        search_query (UnknownBook) : title / author members
        user (UserDetails) : username member
        option (str) : option we are running
    Returns:
        dict[str,str]: keys are script required args `search`, `user`, `option`.
    """
    search_info = search_query.model_dump()
    user_info = user.model_dump()

    author = search_info['author']
    title = search_info['title']

    search_term = f"{title} {author}".strip()

    return {
        "search" : search_term,
        "user" : user_info['username'],
        "option" : option
    }

def format_script_result(result: tuple[bool,str]) -> dict:
    # need to refine script out 
    #assume dict for now ..
    status , data = result
    return {
        'success' : status,
        'payload' : data
    }
        

def load_task_info(file_path: str) -> dict[str,str]:
    """ Read in task information. """
    with open(file_path, 'r') as f:
        return json.load(f)
def move_to_vault(file_details: dict[str,str]) -> str:
    """ 
    Move item to the vault. 
    
    Returns new path or none
    """
    title = file_details.get('title')
    fname = file_details.get('fname')
    lname = file_details.get('lname')
    source = file_details.get('source', None)

    author = f"{fname} {lname}".strip() 
    new_file_path = os.path.join(config.THE_VAULT,'the_goods')
    new_file_name = os.path.join(new_file_path, f"{title} by {author}.epub")
    if source is not None and os.path.exists(source):
        new_path = shutil.move(source,new_file_name)
        return new_path
    return ""

def delete_duplicate(file_details: dict[str,str]):
    """ Used with DB tools , deletes file if already existing in vault. """

    source = file_details['source']
    try:
        if os.path.isfile(source):
            os.remove(source)
            return "delete_delete" # just my own personal flag
    except Exception as e:
        print(f"bad delete {e}")
    return ""

    
def clean_job_listing(*, job_file : str, new_file_path:str =""):
    """ removes the job_file if job is done """
    #gate check for a good delete
    #can't remove new_file_path none check due to confirmation of a good move to vault, we want to save our files until its moved.
    if new_file_path == "delete_delete" or new_file_path and os.path.exists(new_file_path):
        os.remove(job_file)
    
def check_overtime() -> list[str]:
    #check OTJob folder and attempt to run it
    todo_list = [ entry.path for entry in os.scandir(config.THE_JOBS) if entry.is_file() and entry.name.endswith('.json')]
    return todo_list

def create_database_job(str_data:str):
    #takes the file metadata generated from script
    try:
        payload = json.loads(str_data)
    except Exception as e:
        print(f"Bad json response in db job creation, {e}")
        return
    data = payload['metadata']
    username = data.get('username')
    job_file_name = f"{username}_book_{int(time.time())}.json"
    with open(os.path.join(config.THE_JOBS,job_file_name), 'w') as f:
        json.dump(data,f)
    return job_file_name