import pytest
from unittest.mock import patch , MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.automation.auto_bot_search import search_query_input , search_result , bot_search , XPATH

@pytest.fixture
def mock_webdriver():
    with patch("selenium.webdriver.Chrome") as MockWebDriver:
        mock_driver_instance = MagicMock()
        MockWebDriver.return_value = mock_driver_instance
        yield mock_driver_instance

##### SEARCH QUERY INPUT #######


def test_auto_bot_search_input(mock_webdriver):
    mock_search_query = "test_query"
    #need to patch .find_element
    mock_search_field = MagicMock()
    mock_search_button = MagicMock()

    mock_webdriver.find_element.side_effect = lambda by, value : {
        (By.XPATH , XPATH['s_field']) : mock_search_field,
        (By.XPATH , XPATH['s_button']) : mock_search_button
    }.get((by,value),MagicMock())
    
    result = search_query_input(mock_webdriver,mock_search_query)

    assert result is not None #None only returns when error occurs
    assert mock_webdriver.find_element.call_count == 2 # attempted to find exactly 2 specific elements
    mock_search_field.send_keys.assert_called_once_with(mock_search_query)
    mock_search_button.click.assert_called_once()

def raise_no_element(by,value):
    raise NoSuchElementException("missing mocked element")

def test_auto_bot_search_missing_search(mock_webdriver):

    ##### NEED TO MOCK fields maybe
    mock_webdriver.find_element.side_effect = raise_no_element

    result = search_query_input(mock_webdriver, "mock_query")
    assert result is None