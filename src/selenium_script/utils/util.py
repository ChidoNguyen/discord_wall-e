import os
import json
def create_user_save_dir(user: str) -> str:
    """
    Creates a directory named after the requester at environment defined base directory.
    
    Args :
        - requester : str = user's name

    Returns :
        - full path (str) or None
    """
    from src.env_config import config as src_config
    try:
        user_folder_path = os.path.join(src_config.DOWNLOAD_DIR,user)
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
        return user_folder_path
    except Exception as e:
        raise RuntimeError(f"Failed to create user save directory for '{user}' : {e}")

def write_json_file(*,data: list , download_dir: str):
    output_file = "results.json"
    output_path = os.path.join(download_dir,output_file)
    with open(output_path, 'w') as f:
        json.dump(data,f,indent=4)