'''
Data store implementation using application configuration.
'''
from typing import Any

from pandas import DataFrame

from main.core.configuration import ConfigurationService, ConfigurationException
from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.model.evaluation import ATTACK_FEATURE_EVALUATIONS, CONSTRAINT_EVALUATIONS,\
    FEATURE_EVALUATIONS, EvaluationColumn
from main.store.core import DataStoreFactory, DataType

TYPE = 'configuration'

def _extract_values(
        configuration: dict[str, Any],
        result: dict[str, list[int]],
        columns: list[EvaluationColumn],
        suffix: str):
    for column in columns:
        result[column.value].append(int(configuration.get(column.value.replace(suffix, ''), 0)))
    return result

@factory_register(TYPE, DataStoreFactory())
class ConfigurationStore(Singleton):
    '''
    An implementation of the data store that reads pandas
    DataFrames from application configuration.
    '''
    def __init__(self) -> None:
        super().__init__()
        if self.initialised:
            return
        self.initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        '''
        Retrieve the DataFrame from values defined in configuration.
        '''
        if data_type != DataType.EVALUATION:
            raise ConfigurationException(
                'Data type ' + data_type.value + ' not supported for configuration storage')
        if page_title != '':
            raise ConfigurationException('Pagination not supported for configuration storage')
        result: dict[str, list[Any]] = {}
        for column_name in EvaluationColumn:
            result[column_name.value] = []
        configs: dict[str, Any] = ConfigurationService().get_configuration_property(
            'evaluation', default={})
        for model_name in configs:
            result[EvaluationColumn.EVALUATION_NAME.value].append(model_name)
            result = _extract_values(
                configs[model_name].get('weights', {}),
                result,
                FEATURE_EVALUATIONS.keys(),
                '-weight')
            result = _extract_values(
                configs[model_name].get('constraints', {}),
                result,
                CONSTRAINT_EVALUATIONS.keys(),
                '-constraint')
            result = _extract_values(
                configs[model_name].get('attack-evaluation-weights', {}),
                result,
                ATTACK_FEATURE_EVALUATIONS.keys(),
                '-attack-evaluation-weight')
        return DataFrame(result)

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        '''
        Writing is not supported for this implementation of the data store.
        '''
        raise ConfigurationException('Writing not supported for configuration storage')
