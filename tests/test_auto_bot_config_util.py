import pytest
from unittest.mock import patch , MagicMock , mock_open
FAKE_INI_CONTENT = """
[USER]
download_dir : /fake/path
[WEB]
url : https://fakeurl.com
userID : fake_admin
userPass: fake_admin_pass
"""
@patch("configparser.ConfigParser")
@patch("os.path.abspath")
@patch("os.path.dirname")
@patch("os.path.join")
def test_auto_bot_config_data(mock_join,mock_dirname,mock_abspath,mock_config):
    mock_config_get = MagicMock()
    mock_config_read = MagicMock()
    mock_config.get.return_value = mock_config_get
    mock_config.read.return_value = mock_config_read
    import src.automation.book_bot_config
    print()
    print(mock_config.mock_calls)
    print(mock_config.get.mock_calls)
    #print(mock_config.__dict__)
    #Expected Calls
    
