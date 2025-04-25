import os
import json
from dataclasses import dataclass
from src.env_config import THE_VAULT , DB_PATH

cache_filename = 'cache_info.json'
cache_folder_name = 'cache'
watched_folder = 'the_goods'
cache_local = os.path.join(THE_VAULT,cache_folder_name)

#for id building w/o zipping and extracting cursor row factory
@dataclass
class RowKeys:
    id: int
    fname: str
    lname : str
    title : str
    @property
    def author(self):
        return f'{self.fname} {self.lname}'.strip()
    @property
    def filename(self):
        return f'{self.title} by {self.author}.epub'
    
def read_cache_info():
    #check for file and info 
    try:
        with open(os.path.join(cache_local,cache_filename) , 'r') as file:
            return json.load(file)
    except (FileNotFoundError,json.JSONDecodeError):
        return None
    
def update_cache_info(data):
    with open(os.path.join(cache_local,cache_filename),'w') as f:
        json.dump(data,f)

def retrieve_db_info():
    import sqlite3
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT id , title , author_first_name , author_last_name FROM digital_brain')
    results = cursor.fetchall()
    con.close()
    return results

def build_cache_data():
    data = retrieve_db_info()
    #items in data are tuples , unzip and convert to dataclass
    data_dump = [RowKeys(*items) for items in data]
    return data_dump

def build_cache_id_map(cache_data : list[RowKeys]):
    #cache_data is a list of our dataclass
    #for every ID -> 
    id_map = {
        item.id : { 
            'fname' : item.fname,
            'lname' : item.lname,
            'author' :item.author,
            'title' : item.title,
            'filename' : item.filename
            } for item in cache_data
    }
    return id_map
def cache_is_valid(cache_data):
    if cache_data is None:
        return False
    cached_mtime = cache_data.get('mtime')
    cur_mtime = os.path.getmtime(os.path.join(THE_VAULT,watched_folder))
    return cached_mtime == cur_mtime

def get_cache_data():
    cache_data = read_cache_info()
    if cache_is_valid(cache_data):
        print("still good")
        return cache_data
    new_cache = {
        'mtime' : os.path.getmtime(os.path.join(THE_VAULT,watched_folder)),
        'data' : build_cache_id_map(build_cache_data())
    }
    update_cache_info(new_cache)
    return new_cache['data']

def main():
    data = get_cache_data()
    return data

if __name__ == '__main__':
    tmp = main()
