import pytest
import shutil
import os
os.environ["TEST_MODE"] = '1'
from selenium.webdriver.common.by import By
from unittest.mock import patch , MagicMock
from src.automation.auto_bot_setup import create_user_save_dir , auto_bot_driver , homepage , login_page , login_creds_input

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

#@patch("src.automation.auto_bot_setup.download_dir")
def test_user_folder_create_v_one(test_user,mock_tmp_path):
    with patch("src.automation.auto_bot_setup.download_dir", mock_tmp_path):
        #approach patches download_dir with mock obj "mock_download_dir_one"
        #we can set a return value
        #mock_download_dir_one = mock_tmp_path
        #when we call our create_user_save_dir
        #pass it our test fixture username
        #our @Patch replaces the download_dir object normally used with our mocked one
        new_folder = create_user_save_dir(test_user)
        
        #EXPECTATIONS
        expected_folder = os.path.join(mock_tmp_path,test_user)
        
        assert expected_folder == new_folder , 'Folder created in unexpected directory.'
        assert os.path.exists(new_folder) , 'Folder directory does not exist.'
        assert os.path.isdir(new_folder) , 'Folder was not created.'

        shutil.rmtree(new_folder)
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

############## WebDriver Test ##########################
# Need to create a mock of the web driver
# Patch normal webdriver with our mock-up 
######

@pytest.fixture
def mock_driver():
    '''create a mocked webdriver instance'''
    with patch("selenium.webdriver.Chrome") as MockWebDriver: #might need this for linux --> patch("selenium.webdriver.chrome.service.Service")
        driver_instance_mock = MagicMock()
        MockWebDriver.return_value = driver_instance_mock
        yield driver_instance_mock

def test_driver_instance(mock_driver,mock_tmp_path):
    with patch("selenium.webdriver.Chrome") as MockWebDriver:
        MockWebDriver.return_value = mock_driver
        driver = auto_bot_driver(mock_tmp_path)

        mock_driver.execute_cdp_cmd.return_value = {"downloadPath" : mock_tmp_path}

        prefs = driver.execute_cdp_cmd("Page.getDownloadBehavior", {})

        assert driver == mock_driver, 'Driver instance is not properly mocked.'
        MockWebDriver.assert_called_once()
        assert prefs.get("downloadPath") == mock_tmp_path, 'Download directory not set properly.'

#######

@pytest.fixture
def mock_config():
    with patch("configparser.ConfigParser") as MockConfigParser:
        mock_config = MockConfigParser.return_value

        def get_mock(section,key):
            values = {
                ("WEB", "url") : "https://fakeurl.com",
                ("WEB", "userID") : "fake_test_user",
                ("WEB", "userPass") : "fake_pass_word"
            }
            return values.get((section,key),None)
        mock_config.get.side_effect = get_mock
        yield mock_config
def test_mock_config(mock_config):
    assert mock_config.get("WEB","url") == "https://fakeurl.com"
    assert mock_config.get("WEB","userID") == "fake_test_user"
    assert mock_config.get("WEB", "userPass") == "fake_pass_word"
    
def test_homepage_success(mock_driver,mock_config):
    #correct target flag "Z-Library"
    mock_driver.title = "Welcome to Z-Library"

    with patch("configparser.ConfigParser", return_value = mock_config):
        result = homepage(mock_driver)
    assert result is mock_driver , 'Expected web driver object but got None'

def test_homepage_fail(mock_driver,mock_config):
    #correct target flag "Z-Library"
    mock_driver.title = "Bad Title"

    with patch("configparser.ConfigParser", return_value = mock_config):
        result = homepage(mock_driver)
    assert result is None , 'Expected None but got a web driver object'

def test_login_page_navigate(mock_driver):
    #need to build our MagicMock to have our target html elements
    mock_login_link_div = MagicMock()
    mock_anchor_element = MagicMock()

    #mocking up what is returned when "find element" is called 
    mock_driver.find_element.side_effect = lambda by , value : (mock_login_link_div if value == "user-data__sign" else MagicMock())
    mock_login_link_div.find_element.return_value = mock_anchor_element # emulates anchor element nested under our login div
    mock_anchor_element.get_attribute.return_value = "https://fakeurl.com/login"

    result = login_page(mock_driver)

    mock_driver.get.assert_called_once_with("https://fakeurl.com/login")
    assert result is mock_driver, 'Expected web driver but got None'

def test_login_page_navigate_fail(mock_driver):
    mock_driver.find_element.side_effect = Exception('Element not found') #raise our own exception

    result = login_page(mock_driver)

    assert result is None , 'Expected None but got web driver object'

def test_login_creds_input(mock_driver,mock_config):
    mock_form = MagicMock()
    mock_id_entry = MagicMock()
    mock_pass_entry = MagicMock()
    mock_submit_button = MagicMock()
    mock_logout_link = MagicMock()
    #when mock driver looks for form we give it our mock_form
    mock_driver.find_element.side_effect = lambda by, value : (mock_form if value == "form" else MagicMock())
    mock_form.find_element.side_effect = lambda by , value : {
        (By.NAME, "email") : mock_id_entry,
        (By.NAME, "password") : mock_pass_entry,
        (By.TAG_NAME,"button") : mock_submit_button,
        (By.XPATH, "//a[@href='/logout']") : mock_logout_link

    }.get((by,value), MagicMock())
    print("Button mock:" , mock_driver.find_element(By.TAG_NAME, "button"))
    with patch("src.automation.auto_bot_setup.userID",mock_config.get("WEB","userID")) , patch("src.automation.auto_bot_setup.userPass",mock_config.get("WEB","userPass")):
        result = login_creds_input(mock_driver)
    mock_id_entry.send_keys.assert_called_once_with(mock_config.get("WEB","userID"))
    mock_pass_entry.send_keys.assert_called_once_with(mock_config.get("WEB", "userPass"))
    mock_submit_button.click.assert_called_once()
    assert result is mock_driver, "Expected web driver but instead got None"

def test_login_creds_input_fail(mock_driver,mock_config):
    mock_form = MagicMock()
    mock_id_entry = MagicMock()
    mock_pass_entry = MagicMock()
    mock_submit_button = MagicMock()

    #missing logout aspect

    def mock_find_elements(by,value):
        elements = {
            (By.NAME, "email") : mock_id_entry,
            (By.NAME, "password") : mock_pass_entry,
            (By.TAG_NAME,"button") : mock_submit_button
        }
        if (by,value) in elements:
            return elements[(by,value)]
        raise Exception("element not found") #faking no logout element
    mock_driver.find_element.side_effect = lambda by, value : (mock_form if value == "form" else MagicMock())
    mock_form.find_element.side_effect = mock_find_elements

    with patch("src.automation.auto_bot_setup.userID",mock_config.get("WEB","userID")) , patch("src.automation.auto_bot_setup.userPass",mock_config.get("WEB","userPass")):
        result = login_creds_input(mock_driver)
    mock_id_entry.send_keys.assert_called_once_with(mock_config.get("WEB","userID"))
    mock_pass_entry.send_keys.assert_called_once_with(mock_config.get("WEB", "userPass"))
    mock_submit_button.click.assert_called_once()
    assert result is mock_driver, "Expected None on failed login"