'''
Data store implementation that uses CSV files in the local file system.
'''
import os
from pandas import read_csv, DataFrame

from main.core.configuration import ConfigurationException, ConfigurationService
from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.store.core import DataStoreFactory, DataType

TYPE = 'localcsvfile'

def _get_file_name(directory: str, data_type: DataType, page_title: str = '') -> str:
    result = directory + '/'
    result += data_type.value + '.'
    if page_title != '':
        result += page_title + '.'
    result += 'csv'
    return result

@factory_register(TYPE, DataStoreFactory())
class LocalCsvFileStore(Singleton):
    '''
    An implementation of the data store that stores pandas DataFrames
    in CSV files in the local file system.
    '''
    def __init__(self) -> None:
        super().__init__()
        if self.initialised:
            return
        self.directory: str = ConfigurationService().get_configuration_property(
            TYPE + '.directory', '')
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        if not os.path.isdir(self.directory):
            raise ConfigurationException(self.directory + ' is not a directory')
        self.cache: dict[str, DataFrame] = {}
        self.initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        '''
        Read the DataFrame from a CSV file in the local file system.
        '''
        filename: str = _get_file_name(self.directory, data_type, page_title)
        if not os.path.exists(filename):
            return DataFrame()
        if filename in self.cache:
            return self.cache[filename]
        result: DataFrame = read_csv(filename)
        self.cache[filename] = result
        return result

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        '''
        Store the DataFrame in a CSV file in the local file system.
        '''
        filename: str = _get_file_name(self.directory, data_type, page_title)
        self.cache[filename] = data
        with open(filename, 'w', encoding='utf8') as csvfile:
            data.to_csv(csvfile, index=False)
