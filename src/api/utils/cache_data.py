import os
import json
from dataclasses import dataclass, fields, asdict
from typing import Mapping

#config
from src.env_config import config
#util
from src.api.utils.db_util import retrieve_table_data, build_FileInfo, FileInfo, DB_FIELDS
cache_file_name = 'cache_info.json'

@dataclass
class CacheResult:
    id_map : Mapping[int,FileInfo]
    #id_map : dict[int,FileInfo]
    id_list: list[int]

    def __iter__(self):
        return iter(getattr(self,field.name) for field in fields(self))

def _build_CacheResult_dataclass(data:list[FileInfo]):
    """ Builds a CacheResult id_map for our database id entries to its FileInfo counterpart """
    id_map = {int(item.id) : item for item in data}
    id_list = list(id_map)
    return CacheResult(id_map=id_map, id_list=id_list)

def build_new_cache():
    table_entries = retrieve_table_data()
    FileInfo_objects = build_FileInfo(table_entries)
    return _build_CacheResult_dataclass(FileInfo_objects)

def write_cache_data(data: CacheResult):
    update_cache = {
        'mtime': os.path.getmtime(config.THE_GOODS),
        'data' : asdict(data)
    }
    try:
        with open(os.path.join(config.CACHE_FOLDER,cache_file_name), 'w') as f:
            json.dump(
                update_cache,
                fp=f,
                indent=4
            )
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None
    
def _cache_key_check(data:str):
    required_key = ['mtime', 'data']
    if not all(key in data for key in required_key):
        return False
    return True
def _cache_map_check(data:str):
    required_map_keys= ['id_map', 'id_list']
    if not all(key in data for key in required_map_keys):
        return False
    return True
def read_cache_data():
    cache_data_path = os.path.join(config.CACHE_FOLDER,cache_file_name)
    try:
        with open(cache_data_path, 'r') as f:
            raw_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None
    

    return
def get_cache_data(json_transfer:bool = True):
    current_cache_data = read_cache_data()

    #rebuild if bad data
    new_cache_data  = build_new_cache()
    write_cache_data(new_cache_data)

    return None
