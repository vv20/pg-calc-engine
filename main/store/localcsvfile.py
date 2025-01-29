import os
from pandas import read_csv, DataFrame

from main.core.configuration import ConfigurationException, ConfigurationService
from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.store.core import DataStoreFactory, DataType

TYPE = 'localcsvfile'

def get_file_name(directory: str, data_type: DataType, page_title: str = '') -> str:
    result = directory + '/'
    result += data_type.value + '.'
    if page_title != '':
        result += page_title + '.'
    result += 'csv'
    return result

@factory_register(TYPE, DataStoreFactory())
class LocalCsvFileStore(Singleton):
    def __init__(self) -> None:
        super().__init__()
        if self._initialised:
            return
        self.directory: str = ConfigurationService().get_configuration_property(TYPE + '.directory', '')
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        if not os.path.isdir(self.directory):
            raise ConfigurationException(self.directory + ' is not a directory')
        self.cache: dict[str, DataFrame] = {}
        self._initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        filename: str = get_file_name(self.directory, data_type, page_title)
        if not os.path.exists(filename):
            return DataFrame()
        if filename in self.cache:
            return self.cache[filename]
        result: DataFrame = read_csv(filename)
        self.cache[filename] = result
        return result

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        filename: str = get_file_name(self.directory, data_type, page_title)
        self.cache[filename] = data
        with open(filename, 'w') as csvfile:
            data.to_csv(csvfile, index=False)