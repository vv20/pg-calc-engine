from enum import Enum
import logging
from pandas import DataFrame

from main.core.configuration import ConfigurationService
from main.core.factory import Factory

logger = logging.getLogger(__name__)

class DataType(Enum):
    EVALUATION = 'evaluation'
    CACHE = 'cache'
    CHARGED_ATTACK_REFERENCE_DATA = 'charged-attack-reference-data'
    CHARGED_ATTACK_PER_POKEMON_REFERENCE_DATA = 'charged-attack-per-pokemon-reference-data'
    CPM_REFERENCE_DATA = 'cpm-reference-data'
    DELTA = 'delta'
    ENRICHED_LIBRARY = 'enriched-library'
    FAST_ATTACK_REFERENCE_DATA = 'fast-attack-reference-data'
    FAST_ATTACK_PER_POKEMON_REFERENCE_DATA = 'fast-attack-per-pokemon-reference-data'
    LIBRARY = 'library'
    PARTITION = 'partition'
    PARTITION_RESULT = 'partition-result'
    POKEMON_TYPE_REFERENCE_DATA = 'pokemon-type-reference-data'
    RESULT = 'result'
    TYPE_CHART_REFERENCE_DATA = 'type-chart-reference-data'

class DataStoreFactory(Factory):
    def __init__(self) -> None:
        super().__init__()

def read_store(
        data_type: DataType,
        page_title: str = '') -> DataFrame:
    data_store = get_data_store(data_type)
    data: DataFrame = data_store.read_store(data_type, page_title)
    logger.info('Read %d rows of %s data via a %s', len(data), data_type.value, type(data_store))
    return data

def write_store(
        data_type: DataType,
        data: DataFrame,
        page_title: str = '') -> None:
    data_store = get_data_store(data_type)
    data_store.write_store(data_type, data, page_title)
    logger.info('Written %d rows of %s data via a %s', len(data), data_type.value, type(data_store))

def clear_cache(data_type: DataType) -> None:
    data_store: object = get_data_store(data_type)
    data_store._initialised = False
    logger.info('Cleared cache from %s', type(data_store))

def get_data_store(data_type: DataType) -> object:
    store_type: str = ConfigurationService().get_configuration_property('store.' + data_type.value)
    return DataStoreFactory().construct(store_type)