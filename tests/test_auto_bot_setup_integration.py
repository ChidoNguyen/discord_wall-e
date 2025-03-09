import pytest
from unittest.mock import patch , MagicMock
from src.automation.auto_bot_setup import auto_bot

@pytest.fixture
def mock_requester():
    return "test_user"

# auto bot strings together all the individual setup components into 1 function
#create save dir
#create webdriver
#navigate to start page
#pre-load cookies if valid OR login and save cookies
#returns webdriver instance , and save directory created


@patch("src.automation.auto_bot_setup.create_user_save_dir")
@patch("src.automation.auto_bot_setup.auto_bot_driver")
@patch("src.automation.auto_bot_setup.homepage")
@patch("src.automation.auto_bot_setup.login_page")
@patch("src.automation.auto_bot_setup.login_creds_input")
@patch("src.automation.auto_bot_setup.bot_site_cookies.valid_cookies")
@patch("src.automation.auto_bot_setup.bot_site_cookies.load_cookies")
@patch("src.automation.auto_bot_setup.bot_site_cookies.save_cookies")
def test_auto_bot_integration_login(
    mock_save_cookies, mock_load_cookies,mock_valid_cookies,mock_login_creds, mock_login_page,
    mock_homepage, mock_auto_bot_driver, mock_save_dir, mock_requester
):
    mock_save_dir.return_value = "/mock/path"
    mock_auto_bot_driver.return_value= MagicMock(name="MockWebDriver")
    mock_homepage.return_value = mock_auto_bot_driver.return_value
    mock_valid_cookies.return_value = False # need new cookies route
    mock_login_page.return_value = mock_auto_bot_driver.return_value
    mock_login_creds.return_value = mock_auto_bot_driver.return_value

    driver , save_dir = auto_bot(mock_requester)

    #Expected return/ results
    assert driver is not None , "Expected web driver instance but got None"
    assert save_dir == '/mock/path' , "Save directory mismatch"

    #Check function calls
    mock_save_dir.assert_called_once_with(mock_requester)
    mock_auto_bot_driver.assert_called_once_with("/mock/path")
    mock_homepage.assert_called_once_with(mock_auto_bot_driver.return_value)
    mock_valid_cookies.assert_called_once()
    mock_login_page.assert_called_once_with(mock_homepage.return_value)
    mock_login_creds.assert_called_once_with(mock_login_page.return_value)
    mock_save_cookies.assert_called_once_with(mock_login_creds.return_value)

@patch("src.automation.auto_bot_setup.create_user_save_dir")
@patch("src.automation.auto_bot_setup.auto_bot_driver")
@patch("src.automation.auto_bot_setup.homepage")
@patch("src.automation.auto_bot_setup.bot_site_cookies.valid_cookies")
@patch("src.automation.auto_bot_setup.bot_site_cookies.load_cookies")
def test_auto_bot_setup_integration_cookies(
    mock_load_cookies, mock_valid_cookies, mock_homepage, mock_auto_bot,mock_user_save,mock_requester
):
    mock_user_save.return_value = "/mock/path"
    mock_auto_bot.return_value = MagicMock(name="MockWebDriver")
    mock_homepage.return_value = mock_auto_bot.return_value
    mock_valid_cookies.return_value = True #bypasses login id/pass input
    
    driver , save_dir = auto_bot(mock_requester)

    assert driver is not None , "Expected web driver but got None"
    assert save_dir == '/mock/path' , "Save directory mismatch"

    mock_user_save.assert_called_once_with(mock_requester)
    mock_auto_bot.assert_called_once_with("/mock/path")
    mock_homepage.assert_called_once_with(mock_auto_bot.return_value)
    mock_valid_cookies.assert_called_once()
    mock_load_cookies.assert_called_once_with(mock_homepage.return_value)