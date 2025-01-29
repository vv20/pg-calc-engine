from pandas import DataFrame

from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.store.core import DataStoreFactory, DataType

TYPE = 'memory'

def get_cache_key(data_type: DataType, page_title: str) -> str:
    cache_key: str = data_type.value
    if page_title != '':
        cache_key += '.' + page_title
    return cache_key

@factory_register(TYPE, DataStoreFactory())
class InMemoryStore(Singleton):
    def __init__(self) -> None:
        super().__init__()
        if self._initialised:
            return
        self.cache: dict[str, DataFrame] = {}
        self._initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        cache_key = get_cache_key(data_type, page_title)
        if cache_key in self.cache:
            return self.cache[cache_key]
        return DataFrame()

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        cache_key = get_cache_key(data_type, page_title)
        self.cache[cache_key] = data