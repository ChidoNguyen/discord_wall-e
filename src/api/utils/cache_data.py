import os
import json
import asyncio
from dataclasses import dataclass, fields, asdict
from typing import Mapping

#config
from src.env_config import config
#util
from src.api.utils.db_util import retrieve_table_data, build_FileInfo, FileInfo
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
    
def _cache_key_check(data:dict):
    ''' Checks our cache loaded data has the 2 required keys. '''
    required_key = ['mtime', 'data']
    if not all(key in data for key in required_key):
        return False
    return True

def _cache_map_check(data:dict):
    """ Verifies the existence of required keys for the dictionary stored in the read-in cache data key `data` """
    required_map_keys= ['id_map', 'id_list']
    if not all(key in data for key in required_map_keys):
        return False
    return True

def read_cache() -> dict:
    cache_data_path = os.path.join(config.CACHE_FOLDER,cache_file_name)
    try:
        with open(cache_data_path, 'r') as f:
            raw_data = json.load(f)
            return raw_data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {}
    
def verify_cache_structure(data:dict):
    """ verify all keys are present """
    return _cache_key_check(data) and _cache_map_check(data['data'])

def verify_cache(data: dict) -> bool:
    return verify_cache_structure(data) and data['mtime']>= os.path.getmtime(config.THE_GOODS)

async def fetch_catalog_cache(json_transfer:bool = True) -> dict | CacheResult:
    """
    Fetches the cache data for the catalog.

    Args:
        json_transfer (bool): Defaults True -> used to return a formatted dictionary of our cache data. If false return our fetched data in its raw form with custom dataclasses `CacheResult` which has `FileInfo`.
    """

    #chatgpt rec for future changes flexibility
    #leaves room for not being tied into "data" key 
    def to_dict(cache_data:dict):
        return asdict(cache_data['data']) if json_transfer else cache_data
    
    current_cache_data = read_cache()
    if verify_cache(current_cache_data):
        return to_dict(current_cache_data)
    
    #rebuild if bad data
    new_cache_data  = await asyncio.to_thread(build_new_cache)
    write_cache_data(new_cache_data)

    return to_dict({'data': new_cache_data})
