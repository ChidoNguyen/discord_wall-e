import pytest,os
from unittest.mock import patch , mock_open
from src.automation.bot_site_cookies import COOKIES, COOKIES_PATH, valid_cookies, load_cookies, save_cookies

'''
cookies dict - > path and fname
'''

@pytest.fixture
def base_dir(tmp_path):
    return str(tmp_path)

"""
1) cookies exists to be opened
    1a) if not expired load
    1b) if expired act as tho no cookies exists
2) cookies do not exists -> returns False
"""
#patch the "open" process to return valid data
@patch("builtins.open", new_callable = mock_open , read_data ='[{"cookies" : "value"}]')
@patch("os.path.exists" , return_value = True) # fakes that file opening is valid
def test_valid_cookies_exists(mock_exists, mock_open):
    results = valid_cookies()
    assert results == True
    mock_open.assert_called_once_with(f'{COOKIES_PATH}/{COOKIES['fname']}','r')

#opening fails
def test_valid_cookies_none():
    return 

    