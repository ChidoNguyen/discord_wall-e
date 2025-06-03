import json
from dataclasses import dataclass
import os
import shutil
#config
from src.env_config import config
from src.api.models.book_model import UnknownBook , UserDetails
#util
from src.api.utils.db_util import insert_database

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
        

def _load_task_info(file_path: str) -> dict[str,str]:
    """ Read in task information. """
    with open(file_path, 'r') as f:
        return json.load(f)
def _move_to_vault(file_details: dict[str,str]) -> str | None:
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
    return None

async def _register_file(job_details: dict[str,str]) -> str | None:
    """ Attempts to register it into our database and then moves to the vault. """
    #add to db AND move to vault
    try:
        await insert_database(job_details=job_details)
    except Exception as e:
        return None
    
    try:
        file_location = _move_to_vault(job_details)
    except Exception as e:
        return None
    return file_location

async def add_to_catalog(file_path: str):
    #to add to catalog:
    #1) load info 
    #2) register witho ur database
    #3) delete job 
    job_info = _load_task_info(file_path=file_path)
    return await _register_file(job_info)
    
def clean_job_listing(*, job_file : str, new_file_path:str):
    """ removes the job_file if job is done """
    if new_file_path and os.path.exists(new_file_path):
        os.remove(job_file)
    
async def check_overtime() -> list[str]:
    #check OTJob folder and attempt to run it
    todo_list = [ entry.path for entry in os.scandir(config.THE_JOBS) if entry.is_file() and entry.name.endswith('.json')]
    return todo_list

async def overtime_jobs() -> list[str]:
    """
    Checks our overtime folder aka any outstanding tasks that should be executed to give most up to date content. tasks is file i/o behaviours.
    """
    extra_pay_listings = await check_overtime()
    for task in extra_pay_listings:
        new_file_path = await add_to_catalog(task)
        if new_file_path is not None:
            clean_job_listing(job_file=task, new_file_path=new_file_path)

    return []