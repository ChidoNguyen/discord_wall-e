from dataclasses import dataclass
import sqlite3

#config
from src.env_config import config

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

async def insert_database(job_details: dict[str,str]):
    fname = job_details.get('fname')
    lname = job_details.get('lname')
    title = job_details.get('title')
    username = job_details.get('username')

    db_con = sqlite3.connect(config.DB_PATH)
    db_cursor = db_con.cursor()
    insert_or_ignore = "INSERT OR IGNORE INTO digital_brain (title,author_first_name, author_last_name, user) VALUES (?,?,?,?)"
    db_cursor.execute(insert_or_ignore,(title,fname,lname,username))
    db_con.commit()
    db_con.close()

def retrieve_table_data():
    """ Gets all our current database entries. """
    con = sqlite3.connect(config.DB_PATH)
    cursor = con.cursor()
    select_clause = f"SELECT {', '.join(DB_FIELDS)} FROM digital_brain"
    cursor.execute(select_clause)
    results = cursor.fetchall()
    con.close()
    return results

def build_FileInfo(data:list):
    return [FileInfo(*item) for item in data]
