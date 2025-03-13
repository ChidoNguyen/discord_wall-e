import pytest
from unittest.mock import patch , MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException , TimeoutException

import os, time , re

from src.automation.auto_bot_download import rename_book_file , download_progress , download_attempt
#! Rare for a file to have the getctime value; for our case it should only be 1 download at a time shouldn't be an issue
@pytest.fixture
def mock_os():
    #expand if we want to mock more but for now we are mocking os.path.join / getctime/listdir/rename(?)
    with patch("os.path.join") as mock_join , patch("os.path.getctime") as mock_getctime, patch("os.listdir") as mock_listdir, patch("os.rename") as mock_rename:
        yield mock_join , mock_getctime, mock_listdir , mock_rename

@pytest.fixture
def mock_data():
    mock_author = "Aspiring Writer"
    mock_title = "Test Title"
    mock_user_folder = 'mock/location'
    mock_user_dir = ['file1','file2','newest']
    yield mock_title, mock_author , mock_user_folder, mock_user_dir
#### Book File Rename ######
#code flow regex 
# os-related block for getting newest file
# rename

def test_auto_bot_download_rename_file(mock_os):
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
    mock_rename.side_effect = lambda file1,file2 : file2
    result = rename_book_file(mock_book,mock_author,mock_user_folder)
    assert result == True
    mock_join.assert_called()
    mock_listdir.assert_called()
    mock_getctime.assert_called()
    mock_rename.assert_called_once_with(f'{mock_user_folder}/newest',f'{mock_user_folder}/{mock_book} by {mock_author}.epub')

#
def test_auto_bot_download_rename_empty_dir(mock_os,mock_data):
    mock_title , mock_author , mock_folder , mock_dir_files= mock_data
    mock_join, _ , mock_listdir , _ = mock_os
    mock_bad_title = "Te<>*:st T\\itl?e"

    #normal mock_join.side_effect = lambda folder,file : f'{folder}/{file}'
    #simulate fail
    #safe to assume if we mock os.join.path without handling it should generate an error


    result = rename_book_file(mock_title, mock_author,mock_folder)
    #join should not be called
    #list is called once
    mock_join.assert_not_called()
    mock_listdir.assert_called_once()
    assert result == False

####### Download Progress #####

def test_auto_bot_download_completion(mock_os,mock_data):
    _ , _ , mock_listdir , _ = mock_os
    _ , _ , mock_folder , mock_files = mock_data

    mock_listdir.return_value = mock_files

    #
    result = download_progress(mock_folder)
    assert result == True
    mock_listdir.assert_called_once_with(mock_folder)

def test_auto_bot_download_fail(mock_os,mock_data):
    _ , _ , mock_listdir , _ = mock_os
    _ , _ , mock_folder , mock_files = mock_data
    mock_files.append('newer.crdownload')
    mock_listdir.return_value = mock_files
    result = download_progress(mock_folder,timeout_limit=1)
    assert result == False


#### Download Attempt ######
@patch("selenium.webdriver.Chrome")
@patch("selenium.webdriver.support.expected_conditions")
@patch("selenium.webdriver.support.wait.WebDriverWait")
def test_auto_bot_download_initiation(mock_wait,mock_EC,mock_driver,mock_data):
    mock_url = "https://test.com"
    mock_title, mock_author , mock_folder , _ = mock_data
    #DYNAMIC CHANGES SOMETIMES
    title_xpath = '//h1[@itemprop= "name"]'
    author_xpath = '//a[@class= "color1"][@title="Find all the author\'s book"]'
    mock_download_button = MagicMock()
    mock_title_element = MagicMock()
    mock_author_element = MagicMock()
    
    mock_driver.find_element.side_effect = lambda by,value :{
        (By.XPATH, title_xpath) : mock_title_element,
        (By.XPATH, author_xpath) : mock_author_element,
        (By.CSS_SELECTOR, "a.btn.btn-default.addDownloadedBook") : mock_download_button
    }.get((by,value), None)

    #mock_wait.return_value = mock_driver
    mock_wait.until.side_effect = lambda condition: condition((By.CSS_SELECTOR,"a.btn.btn-default.addDownloadedBook"))
    mock_EC.presence_of_element_located.return_value = mock_download_button
    with patch("src.automation.auto_bot_download.download_progress", return_value = True), patch("src.automation.auto_bot_download.rename_book_file", return_value=True):
        result = download_attempt(mock_driver,mock_url,mock_folder)
        assert result is mock_driver
        print()
        print(mock_driver.mock_calls)
        print(mock_wait.until.mock_calls)
        print(mock_EC.mock_calls)
        print(mock_download_button.mock_calls)
    return
    



    
