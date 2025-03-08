import pytest , os
os.environ["TEST_MODE"] = '1'
import sys
print(sys.path)
from unittest.mock import patch
from src.automation.auto_bot_setup import create_user_save_dir

'''
with patch -> better for block code testing ( context manager)
@patch -> better for entire test script (Decorator)

notes to self:
@patch checks arguments from RIGHT to LEFT filling for pytest.fixtures or decorators first
if single patching
e.g. 
@patch(mock.d)
@patch(mock.c)
@patch(mock.b)
@patch(mock.a)
if multi patching : @patch(mock.a,mock.b, mock.c, mock.d)
test_func(a,b,c,d,pytest_e):
    code

patch -> used to replace a target in code
mock -> creates an object that allows us to track for better testing info
    -> for ex: dictate what return values or check how many times its called
'''



# we create our own temporary path fixture to be used throughout the tests
@pytest.fixture
def mock_tmp_path(tmp_path):
    return str(tmp_path)
@pytest.fixture
def test_user():
    return "beeboopTest"

#I want to test folder creation to pre-load into chrome webdriver
#OG Function takes 1 argument the users "name" to create folder name
#OG Function utilizes config file to extract parent "download_dir" to create new folder under
#To-do: Need to patch the OG Download_Dir 

@patch("scripts.auto_bot_setup.download_dir")
def test_user_folder_create_v_one(mock_download_dir_one,test_user,mock_tmp_path):
    #approach patches download_dir with mock obj "mock_download_dir_one"
    #we can set a return value
    mock_download_dir_one.return_value = mock_tmp_path
    #when we call our create_user_save_dir
    #pass it our test fixture username
    #our @Patch replaces the download_dir object normally used with our mocked one
    new_folder = create_user_save_dir(test_user)
    
    #EXPECTATIONS
    expected_folder = os.path.join(mock_download_dir_one,test_user)
    
    assert expected_folder == new_folder , 'Folder created in unexpected directory.'
    assert os.path.exists(new_folder) , 'Folder directory does not exist.'
    assert os.path.isdir(new_folder) , 'Folder was not created.'

""" 
This approach does not work because new_callable is ran at patch-time before pytest injects--
---so "mock_tmp_dir" is undefined at time of new_callable attempt
@patch("scripts.auto_bot_setup.download_dir", new_callable = lambda : mock_tmp_path)
def test_user_folder_create_v_two(mock_download_dir_two,test_user):
    #approach patches download_dir, when it is used w/o needing to edit mock_download_dir_two object
    new_folder = create_user_save_dir(test_user)
    #EXPECTATIONS
    expected_folder = os.path.join(mock_download_dir_two,test_user)
    
    assert expected_folder == new_folder , 'Folder created in unexpected directory.'
    assert os.path.exists(new_folder) , 'Folder directory does not exist.'
    assert os.path.isdir(new_folder) , 'Folder was not created.'
 """
#smaller scoped patch that is not persistent thru whole testing script
def test_user_folder_creation(tmp_path):
    test_requester = "robboTest"
    fake_download_dir = str(tmp_path)
    with patch("scripts.auto_bot_setup.download_dir",fake_download_dir):
        user_folder = create_user_save_dir(test_requester)
        
        #Expectation : folder to be created
        expected_path = os.path.join(fake_download_dir,test_requester)

        #path creation string check
        #path exists
        #path is a folder and not file
        assert user_folder == expected_path
        assert os.path.exists(user_folder)
        assert os.path.isdir(user_folder)


