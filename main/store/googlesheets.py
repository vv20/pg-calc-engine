'''
Data store implementation using the Google Sheets API.
'''
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from pandas import DataFrame

from main.core.configuration import ConfigurationService, ConfigurationException
from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.store.core import DataStoreFactory, DataType

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def _login() -> Credentials:
    creds: Credentials = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w', encoding='utf8') as token:
            token.write(creds.to_json())
    return creds

@factory_register('googlesheets', DataStoreFactory())
class GoogleSheetsStore(Singleton):
    '''
    An implementation of the data store that reads pandas
    DataFrames from Google Sheets spreadsheets.
    '''
    def __init__(self) -> None:
        super().__init__()
        if self.initialised:
            return
        self.credentials: Credentials = _login()
        self.sheets_service: Resource = build(
            'sheets', 'v4', credentials=self.credentials).spreadsheets()
        self.initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        '''
        Retrieve the DataFrame from data in a Google Sheets spreadsheet.
        '''
        if page_title != '':
            raise ConfigurationException('Pagination not supported for Google Sheets storage')
        spreadsheet_id: str = ConfigurationService().get_configuration_property(
            'googlesheets.' + data_type.value + '.spreadsheet')
        sheet_name: str = ConfigurationService().get_configuration_property(
            'googlesheets.' + data_type.value + '.sheetname')
        range_name: str = ConfigurationService().get_configuration_property(
            'googlesheets.' + data_type.value + '.range')
        result = (
            self.sheets_service.values()
            .get(spreadsheetId=spreadsheet_id, range=sheet_name + '!' + range_name)
            .execute()
        )
        values: list = result.get('values', [])
        return DataFrame(columns=values[0], data=values[1:])

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        '''
        Writing is not supported for this implementation of the data store.
        '''
        raise ConfigurationException('Writing not supported for Google Sheets storage')
