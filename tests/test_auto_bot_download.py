import pytest
from unittest.mock import patch , MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , TimeoutException

import os, time , re

from src.automation.auto_bot_download import rename_book_file

@pytest.fixture
def mock_os():
    #expand if we want to mock more but for now we are mocking os.path.join / getctime/listdir/rename(?)
    with patch("os.path.join") as mock_join , patch("os.path.getctime") as mock_getctime, patch("os.listdir") as mock_listdir, patch(os.rename) as mock_rename:
        yield mock_join , mock_getctime, mock_listdir , mock_rename
#### Book File Rename ######
#code flow regex 
# os-related block for getting newest file
# rename

def test_auto_book_download_rename_file(mock_os):
    #regex to make new book title if needed
    mock_join , mock_getctime , mock_listdir , mock_rename= mock_os
    mock_book = "Proper Book Title"
    mock_author = "Aspiring Writer"

    #fake our dir
    mock_user_folder = "mock/location"
    mock_files_dir = ['file1', 'file2', 'newest']

    #
    mock_join.side_effect = lambda folder,file : f'{folder}/{file}'
    mock_getctime.side_effect = lambda filepath: 999 if filepath.endswith('newest') else 111
    mock_listdir.return_value = mock_files_dir
    mock_rename.side_effect = lambda old_name , new_name:           mock_files_dir[-1] = new_name
    result = rename_book_file(mock_book,mock_author,mock_user_folder)
    assert result == True
    return

