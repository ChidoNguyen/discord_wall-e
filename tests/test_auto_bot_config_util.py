import pytest
from unittest.mock import patch , MagicMock , mock_open , PropertyMock
from selenium.webdriver.common.by import By
from src.automation.auto_bot_util import navigate_download_history  , check_download_limit
FAKE_INI_CONTENT = """
[USER]
download_dir : /fake/path
[WEB]
url : https://fakeurl.com
userID : fake_admin
userPass: fake_admin_pass
"""
@patch("os.path.abspath")
@patch("os.path.dirname")
@patch("os.path.join")
def test_auto_bot_config_data(mock_join,mock_dirname,mock_abspath):
    with patch("configparser.ConfigParser.read") as mock_cfg_read, patch("configparser.ConfigParser.get") as mock_cfg_get:
        import src.automation.book_bot_config
        #print()
        #print(mock_cfg_get.mock_calls)
        #print(mock_cfg_read.mock_calls)
        #Expected Calls
        expected_gets = [
            (("USER","download_dir"),),
            (("WEB", "url"),),
            (("WEB", "userID"),),
            (("WEB", "userPass"),)
        ]
        mock_cfg_read.assert_called_once()
        assert mock_cfg_get.call_count == 4 #change based on config items
        mock_cfg_get.assert_has_calls(expected_gets,any_order=True)
    
@pytest.fixture
def mock_driver():
    with patch("selenium.webdriver.Chrome") as web_driver:
        yield web_driver

def test_auto_bot_util_navigate_download_history(mock_driver):
    mock_link = MagicMock()
    mock_driver.find_element.side_effect = lambda by,value : mock_link if (by,value) == (By.XPATH,"//a[@href='/users/downloads']") else None
    mock_link.get_attribute.side_effect = lambda attr : 'https://fakelink.com' if attr == 'href' else ""
    mock_driver.get.side_effect = mock_driver

    result = navigate_download_history(mock_driver)
    assert result is mock_driver
    mock_driver.find_element.assert_called_once_with(By.XPATH, "//a[@href='/users/downloads']")
    mock_driver.get.assert_called_once()
    mock_link.get_attribute.assert_called_once_with('href')

def test_auto_bot_util_download_limit(mock_driver):
    mock_ten_limit = MagicMock()
    #type(mock_ten_limit).text = PropertyMock(return_value= "10/10")

    text_prop_mock = PropertyMock(return_value="10/10")
    type(mock_ten_limit).text = text_prop_mock

    limit_css = (By.CSS_SELECTOR, "div.m-v-auto.d-count")
    mock_driver.find_element.side_effect = lambda by,value : mock_ten_limit if (by,value) == limit_css else None

    result = check_download_limit(mock_driver)
    assert result == True
    mock_driver.find_element.assert_called_once_with(limit_css[0],limit_css[1])
    assert text_prop_mock.call_count == 1


    
    