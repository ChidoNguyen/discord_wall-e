import os
import json
from dataclasses import dataclass , asdict
from src.env_config import THE_VAULT , DB_PATH
########
cache_data_filename = 'cache_info.json'
cache_folder = os.path.join(THE_VAULT,'cache') #os env later
watched_folder = os.path.join(THE_VAULT,'the_goods') #os env later as well



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
    
@dataclass
class CacheResult:
    id_map : dict[int,FileInfo]
    id_list: list[int]

def retrieve_db_info():
    import sqlite3
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    select_clause = f"SELECT {', '.join(DB_FIELDS)} FROM digital_brain"
    cursor.execute(select_clause)
    results = cursor.fetchall()
    con.close()
    return results

def read_cache_info(cache_file = os.path.join(cache_folder,cache_data_filename)):
    try:
        with open(cache_file , 'r') as file:
            raw =  json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    #key check
    req_key = ['mtime' , 'data']
    if not all(key in raw for key in req_key):
        return None
    
    raw_data = raw['data']

    #key check
    req_data_key = ['id_map','id_list']
    if not all(key in raw_data for key in req_data_key):
        return None
    try:
        raw_id_map = {
            int(k) : FileInfo(**v) for (k,v) in raw_data['id_map'].items()
        }
    except (TypeError,ValueError) :
        return None

    cached_result = CacheResult(id_map=raw_id_map , id_list=raw_data['id_list'])

    loaded_cache = {
        'mtime' : raw['mtime'],
        'data' : cached_result
    }
    return loaded_cache

def valid_cache(cache_data):
    return cache_data['mtime'] == os.path.getmtime(watched_folder)
    
def write_cache_data(new_cache , cache_file = os.path.join(cache_folder,cache_data_filename)):
    upd_cache = {
        'mtime' : os.path.getmtime(watched_folder),
        'data' : asdict(new_cache)
    }
    try:
        with open(cache_file , 'w') as file:
            json.dump(
                upd_cache,
                fp=file,indent=4
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get_db_data():
    import sqlite3
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute('SELECT id , title , author_first_name , author_last_name FROM digital_brain')
    results = cursor.fetchall()
    con.close()
    return results

def build_new_cache():
    db_info = retrieve_db_info()

    file_info = [FileInfo(*item) for item in db_info]

    id_map = {int(item.id) : item for item in file_info}
    id_list = list(id_map)

    return CacheResult(id_map=id_map,id_list=id_list)

def get_cache_data(json_transfer = True):
    #read in what we have
    #verify
    cur_data = read_cache_info()
    if cur_data is not None and valid_cache(cur_data):
        return  asdict(cur_data['data']) if json_transfer else cur_data['data']
    new_cache = build_new_cache()
    write_cache_data(new_cache)
    return asdict(new_cache) if json_transfer else new_cache
    
if __name__ == '__main__':
    tmp = get_cache_data(json_transfer=False)
    print(tmp)