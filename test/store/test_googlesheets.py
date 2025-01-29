from googleapiclient.discovery import Resource
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pandas import DataFrame
import pytest
from unittest.mock import call, patch, mock_open, MagicMock

from main.store import clear_cache, read_store, write_store, DataType

from test.util import framework_setup

# Mock data for testing
MOCK_TOKEN = '{\'token\': \'mock_token\'}'
MOCK_VALUES = {
    'values': [
        ['Header1', 'Header2', 'Header3'],
        ['Row1Col1', 'Row1Col2', 'Row1Col3'],
        ['Row2Col1', 'Row2Col2', 'Row2Col3'],
    ]
}

@pytest.fixture
def googlesheets_setup(mocker):
    mock_creds_from_file = mocker.patch('main.store.googlesheets.Credentials.from_authorized_user_file')
    mock_creds = MagicMock(spec=Credentials)
    mock_creds.universe_domain = 'googleapis.com'
    mock_creds.valid = True
    mock_creds.to_json.return_value = MOCK_TOKEN
    mock_creds_from_file.return_value = mock_creds

    mock_flow = MagicMock(spec=InstalledAppFlow)
    mock_flow.run_local_server.return_value = mock_creds
    mock_flow_from_secrets_file = mocker.patch('main.store.googlesheets.InstalledAppFlow.from_client_secrets_file')
    mock_flow_from_secrets_file.return_value = mock_flow

    mock_build = mocker.patch('main.store.googlesheets.build')
    mock_sheets_service = MagicMock(spec=Resource)
    mock_sheets_service.values = MagicMock()
    mock_values = mock_sheets_service.values.return_value
    mock_values.get.return_value.execute.return_value = MOCK_VALUES
    mock_build.return_value.spreadsheets.return_value = mock_sheets_service

    mock_request = mocker.patch('main.store.googlesheets.Request')

    open_mock = mocker.patch('main.store.googlesheets.open', new_callable=mock_open, read_data=MOCK_TOKEN)

    yield {
        'mock_creds_from_file': mock_creds_from_file,
        'mock_creds': mock_creds,
        'mock_flow': mock_flow,
        'mock_flow_from_secrets_file': mock_flow_from_secrets_file,
        'mock_values': mock_values,
        'mock_request': mock_request,
        'open_mock': open_mock
    }

@patch('main.store.googlesheets.os.path.exists', return_value=True)
def test_login_with_cached_token(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    mock_creds_from_file = googlesheets_setup['mock_creds_from_file']

    read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)

    mock_path_exists.assert_any_call('token.json')
    mock_creds_from_file.assert_has_calls([
        call('token.json', ['https://www.googleapis.com/auth/spreadsheets.readonly']),
        call('token.json', ['https://www.googleapis.com/auth/spreadsheets.readonly'])])

@patch('main.store.googlesheets.os.path.exists', return_value=False)
def test_login_without_cached_token(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    mock_flow = googlesheets_setup['mock_flow']
    mock_flow_from_secrets_file = googlesheets_setup['mock_flow_from_secrets_file']
    open_mock = googlesheets_setup['open_mock']

    read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)

    mock_flow_from_secrets_file.assert_called_once_with(
        'credentials.json', ['https://www.googleapis.com/auth/spreadsheets.readonly'])
    mock_flow.run_local_server.assert_called_once_with(port=0)
    open_mock.return_value.write.assert_called_once_with(MOCK_TOKEN)

@patch('main.store.googlesheets.os.path.exists', return_value=True)
def test_login_with_expired_token(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    mock_creds = googlesheets_setup['mock_creds']
    mock_request = googlesheets_setup['mock_request']
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = True

    read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)

    mock_creds.refresh.assert_called_once_with(mock_request.return_value)

@patch('main.store.googlesheets.os.path.exists', return_value=True)
def test_google_sheets_store_read_store(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    mock_values = googlesheets_setup['mock_values']

    df = read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)

    mock_values.get.assert_called_once_with(
        spreadsheetId='abcde12345',
        range='Charged Attacks!A1:D250',
    )

    expected_df = DataFrame(
        columns=['Header1', 'Header2', 'Header3'],
        data=[
            ['Row1Col1', 'Row1Col2', 'Row1Col3'],
            ['Row2Col1', 'Row2Col2', 'Row2Col3'],
        ],
    )
    assert df.equals(expected_df)

@patch('main.store.googlesheets.os.path.exists', return_value=True)
def test_google_sheets_store_read_store_with_page_title(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    with pytest.raises(Exception, match='Pagination not supported for Google Sheets storage'):
        read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA, page_title='page-title')

@patch('main.store.googlesheets.os.path.exists', return_value=True)
def test_google_sheets_store_write_store(mock_path_exists, framework_setup, googlesheets_setup):
    clear_cache(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    with pytest.raises(Exception, match='Writing not supported for Google Sheets storage'):
        write_store(DataType.CHARGED_ATTACK_REFERENCE_DATA, DataFrame())