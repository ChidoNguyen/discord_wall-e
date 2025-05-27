import os
import time
import shutil

from src.selenium_script.utils import epub_util
#user_folder: str = ""

# download related util :
# -- waits/poll for "finished" with proper time-out set
# -- renames if successful
def get_folder_snapshot(*,user_folder: str, key: str = "") -> set:
    """ Provides a set[str] of current files in folder. 
        key : used to set what os.DirEntry attribute 
        currently only path, or left empty to default the whole object.
    """
    # scandir over listdir , for overhead, metadata (later) , iterative vs listdir loading full

    #need to filter out .tmp extension files#
    def is_valid_file(dir_entry: os.DirEntry):
        return dir_entry.is_file() and not dir_entry.name.endswith('.tmp')
    
    if key == 'path':
        return {dir_item.path for dir_item in os.scandir(user_folder) if is_valid_file(dir_item)}
    
    return {dir_item for dir_item in os.scandir(user_folder) if is_valid_file(dir_item)}

def _check_download(*,user_folder:str, old_files: set[str],timeout_limit: int = 60) -> bool:
    """ Polls user download directory for in progress download remnants. 
    Returns bool for download status
    """
    timeout_counter = 0
    # need to buy time for driver to have "new/temp" download file populate
    max_wait_for_new = 5 #seconds
    poll_rate = .5
    while max_wait_for_new > 0:
        new_snapshot = get_folder_snapshot(user_folder=user_folder,key="path")
        new_files = new_snapshot.difference(old_files)
        if new_files:
            break
        max_wait_for_new -= poll_rate
        time.sleep(poll_rate)
    else:
        #aka if no new files reutrn false
        return False #  else for "WHILE" needs break or else it'll trigger
    
    new_file = new_files.pop()
    # might have finished by the time script arrives here
    #return early 
    if os.path.exists(new_file) and not new_file.endswith('.crdownload'):
        return True
    #poll 
    while timeout_counter < timeout_limit:
        if not os.path.exists(new_file):
            return True
        timeout_counter += 1
        time.sleep(1)
    return False

def _get_newest(*,download_path:str) -> str:
    """ Gets the newest file aka our download """
    """ files_in_dir = [ os.path.join(download_path,files) for files in os.listdir(download_path)]
    newest_file = max(files_in_dir, key=os.path.getctime)  """
    ### os.scandir() approach ? ####
    all_files: set[os.DirEntry] = get_folder_snapshot(user_folder=download_path)
    #with os.path.. Can call "os.path.getctime()" on each entry being passed in as param
    # os.scandir entries, stat is a method of the class use lambda
    newest_file = max(all_files, key= lambda f: f.stat().st_ctime)
    return newest_file.path if newest_file else ''

def _rename_file(*,download_dir: str,file_path:str, data: dict[str,str]):

    author = f"{data['fname']} {data['lname']}".strip()
    new_title = f"{data['title']} by {author}.epub"
    new_source = shutil.move(file_path,os.path.join(download_dir,new_title))
    #add source key : value to our data dictionary
    data['source'] = f'{new_source}.finish'
    
def rename_download(*,download_path: str) -> dict[str,str]:

    target_file_path = _get_newest(download_path=download_path)
    if not target_file_path:
        raise RuntimeError("Empty directory for new downloads.")
    

    try:
        file_metadata = epub_util.get_meta_data(file_path=target_file_path)
    except Exception as e:
        raise RuntimeError("Could not parse file metadata.") from e
    
    try:
        _rename_file(download_dir= download_path,file_path=target_file_path,data=file_metadata)
        return file_metadata
    except Exception as e:
        raise RuntimeError("Could not rename file.") from e
    
def check_download_status(*,user_folder:str,old_files: set[str]):
    return _check_download(user_folder=user_folder,old_files=old_files)

def results_out():
    """ json_object = {
            'link' : url,
            'author' : author,
            'title' : title
        }
        json_data.append(json_object)
    
    with open(os.path.join(user_folder,'results.json'),'w') as json_file:
        json.dump(json_data,json_file,indent=4)
    return True """
    