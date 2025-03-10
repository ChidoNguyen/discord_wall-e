import pytest,os,time
from unittest.mock import patch , mock_open , MagicMock
from src.automation.bot_site_cookies import COOKIES, COOKIES_PATH, valid_cookies, load_cookies, save_cookies

'''
cookies dict - > path and fname
'''

@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)
@pytest.fixture
def expected_path():
    return os.path.join(COOKIES_PATH,COOKIES['fname'])
@pytest.fixture
def mock_webdriver():
    with patch("selenium.webdriver.Chrome") as MockWebDriver:
        driver_instance_mock = MagicMock()
        MockWebDriver.return_value = driver_instance_mock
        yield driver_instance_mock
"""
1) cookies exists to be opened
    1a) if not expired load
    1b) if expired act as tho no cookies exists
2) cookies do not exists -> returns False
"""

############### VALID_COOKIES##################

#patch the "open" process to return valid data
@patch("builtins.open", new_callable = mock_open , read_data ='[{"cookies" : "value"}]')
@patch("os.path.exists" , return_value = True) # fakes that file opening is valid
def test_valid_cookies_exists(mock_exists, mock_open,expected_path):
    results = valid_cookies()
    assert results == True
    mock_open.assert_called_once_with(expected_path,'r')

#opening fails file does not exist
@patch("builtins.open")
@patch("os.path.exists" , return_value = False)
def test_valid_cookies_none(mock_exists, mock_open,expected_path):
    result = valid_cookies()
    assert result == False
    mock_open.assert_called_once_with(expected_path,'r')
    
#opening works but expired cookies

@patch("builtins.open" , new_callable= mock_open, read_data = '[{"cookies": "values" , "expiry" : 1111 },{"cookies": "values" , "expiry" : 1111 }]')
@patch("os.path.exists" , return_value = True)
@patch("time.time", return_value = 99999999999)
def test_valid_cookies_expired(mock_time,mock_exists, mock_open,expected_path):
    result = valid_cookies()
    assert result == False
    mock_open.assert_called_once_with(expected_path , 'r')


################# LOAD_COOKIES ###################

#loads pre-existing cookies into webdriver
#1) opens file
#2) loads cookies
#3) refresh driver
#patch targets : os.path.exists for use with join
#               mock_open for json files
#               mock driver add_cookie()

@patch("builtins.open",new_callable=mock_open, read_data = '[{"cookies": "values" , "expiry" : 1111 },{"cookies": "values" , "expiry" : 1111 }]')
@patch("os.path.exists", return_value=True)
def test_load_cookies(mock_exists, mock_open, mock_webdriver,expected_path):
    mock_webdriver.add_cookie = MagicMock() #MagicMock() used to "mock method" to behave like normal ... side_effect if we want specific returns
    result = load_cookies(mock_webdriver)
    assert result == True
    mock_open.assert_called_once_with(expected_path,'r')
    assert mock_webdriver.add_cookie.call_count == 2 #we have 2 items in mock read_data that should be added
    mock_webdriver.refresh.assert_called_once()


########## SAVE_COOKIES ##################
# success // no file // no dump

@patch("builtins.open", new_callable=mock_open)
def test_save_cookies(mock_open,mock_webdriver,expected_path):
    mock_webdriver.get_cookies.side_effect = '[{"cookies": "values" , "expiry" : 1111 },{"cookies": "values" , "expiry" : 1111 }]'
    result = save_cookies(mock_webdriver)

    assert result is None #function returns nothing
    mock_open.assert_called_once_with(expected_path , 'w')
    mock_open().write.assert_called()

