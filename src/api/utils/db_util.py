from dataclasses import dataclass
import sqlite3
#config
from src.env_config import config
#util
from src.api.utils.book_route_util import load_task_info, move_to_vault, clean_job_listing
#for id_map building w/o zipping and extracting cursor row factory
DB_FIELDS = ('id','title','author_first_name','author_last_name')
@dataclass
class FileInfo:
    id: int
    title: str
    fname: str
    lname : str
    @property
    def author(self):
        return f'{self.fname} {self.lname}'.strip()
    @property
    def filename(self):
        return f'{self.title} by {self.author}.epub'

def insert_database(all_jobs: list[str]):
    """     fname = job_details.get('fname')
    lname = job_details.get('lname')
    title = job_details.get('title')
    username = job_details.get('username')
    """
    '''
    Insert items into our db on 1 connection
    '''
    #open
    insert_or_ignore = "INSERT OR IGNORE INTO digital_brain (title,author_first_name, author_last_name, user) VALUES (?,?,?,?)"
    with sqlite3.connect(config.DB_PATH) as db_con:
        db_cursor = db_con.cursor()
        #looped tasks off our jobs
        for job_details in all_jobs:        
            job = load_task_info(job_details)
        
            db_cursor.execute(insert_or_ignore,(
                job.get('title'),
                job.get('fname'),
                job.get('lname'),
                job.get('user')
                ))
            
            if db_cursor.rowcount > 0:
                new_file_path = move_to_vault(job)
                clean_job_listing(job_file = job_details, new_file_path= new_file_path)


def retrieve_table_data():
    """ Gets all our current database entries. """
    with sqlite3.connect(config.DB_PATH) as con:
        cursor = con.cursor()
        select_clause = f"SELECT {', '.join(DB_FIELDS)} FROM digital_brain"
        cursor.execute(select_clause)
        return cursor.fetchall()


def build_FileInfo(data:list):
    return [FileInfo(*item) for item in data]

