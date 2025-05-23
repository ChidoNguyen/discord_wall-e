import os
import time
import shutil

from src.selenium_script.utils import epub_util
#user_folder: str = ""

# download related util :
# -- waits/poll for "finished" with proper time-out set
# -- renames if successful

def _check_download(*,user_folder:str,timeout_limit: int = 60) -> bool:
    """ Polls user download directory for in progress download remnants. 
    Returns bool for download status
    """
    download_incomplete = True
    timeout_counter = 0

    while download_incomplete and timeout_counter < timeout_limit:
        download_incomplete = False
        for file_names in os.listdir(user_folder):
            download_incomplete = file_names.endswith('.crdownload')
        timeout_counter += 1
        time.sleep(1)

    return not download_incomplete

def _get_newest(*,download_path:str) -> str:
    """ Gets the newest file aka our download """
    files_in_dir = [ os.path.join(download_path,files) for files in os.listdir(download_path)]
    newest_file = max(files_in_dir, key=os.path.getctime) 
    return newest_file

def _rename_file(*,download_dir: str,file_path:str, data: dict[str,str]):

    author = f"{data['fname']} {data['lname']}".strip()
    new_title = f"{data['title']} by {author}.epub"
    new_source = shutil.move(file_path,os.path.join(download_dir,new_title))
    return {
        'source' : f'{new_source}.finish',
        'title' : data['title'],
        'fname' : data['fname'],
        'lname' : data['lname']
    } #might need user name...
    
def rename_download(*,download_path: str):
    
    
    try:
        target_file_path = _get_newest(download_path=download_path)
    except:
        return

    try:
        file_metadata = epub_util.get_meta_data(file_path=target_file_path)
    except Exception as e:
        raise RuntimeError("Could not parse file metadata.") from e
    
    try:
        file_info = _rename_file(download_dir= download_path,file_path=target_file_path,data=file_metadata)
        return file_info
    except:
        return
    
def download_status(*,user_folder:str):
    return _check_download(user_folder=user_folder)
    