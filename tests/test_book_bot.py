import pytest, sys, os
from unittest.mock import MagicMock, patch
from src.automation.book_bot import book_bot
'''
bot initialized with system arguments : --search , --user, --option
args parsed
start webdriver
start search
start download
---secondary usage:
user dictates which link skip straight to download
'''

@pytest.fixture
def mock_driver():
    with patch("selenium.webdriver.Chrome") as mock_driver:
        yield mock_driver
@pytest.fixture()
def mock_sysargs():
    with patch("src.automation.book_bot.arg_parse", return_value = ("test_user" , "test_search" , "getbook")) as mock_args:
        yield mock_args

def test_book_bot_success_getbook(mock_driver,mock_sysargs):
    mock_driver.side_effect = mock_driver
    
    with patch('src.automation.book_bot.auto_bot', return_value = True), patch('src.automation.book_bot.max_limit', return_value = True):
        result = book_bot()
        
if __name__ == '__main__':
    x = lambda a : print("adjusting book bot sys arg approach")
