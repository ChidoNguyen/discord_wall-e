
import sqlite3
#config
from src.env_config import config



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
