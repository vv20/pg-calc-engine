from pandas import DataFrame
from typing import Any

from main.core.configuration import ConfigurationService
from main.core.factory import factory_register
from main.core.singleton import Singleton
from main.model.evaluation import EvaluationColumn
from main.store.core import DataStoreFactory, DataType

TYPE = 'configuration'

@factory_register(TYPE, DataStoreFactory())
class ConfigurationStore(Singleton):
    def __init__(self) -> None:
        super().__init__()
        if self._initialised:
            return
        self._initialised = True

    def read_store(self, data_type: DataType, page_title: str = '') -> DataFrame:
        if data_type != DataType.EVALUATION:
            raise Exception('Data type ' + data_type.value + ' not supported for configuration storage')
        if page_title != '':
            raise Exception('Pagination not supported for configuration storage')
        result: dict[str, list[Any]] = {}
        for column_name in EvaluationColumn:
            result[column_name.value] = []
        evaluation_configurations: dict[str, Any] = ConfigurationService().get_configuration_property('evaluation', default={})
        for model_name in evaluation_configurations:
            result[EvaluationColumn.EVALUATION_NAME.value].append(model_name)
            weights_configuration: dict[str, Any] = evaluation_configurations[model_name].get('weights', {})
            constraints_configuration: dict[str, Any] = evaluation_configurations[model_name].get('constraints', {})
            attack_evaluation_weights_configuration: dict[str, Any] = evaluation_configurations[model_name].get('attack-evaluation-weights', {})
            for weight_column_name in weights_configuration:
                weight = int(weights_configuration.get(weight_column_name, 0))
                result[weight_column_name + '-weight'].append(weight)
            for constraint_column_name in constraints_configuration:
                constraint = int(constraints_configuration.get(constraint_column_name, 0))
                result[constraint_column_name + '-constraint'].append(constraint)
            for attack_evaluation_weight_column_name in attack_evaluation_weights_configuration:
                attack_evaluation_weight = int(attack_evaluation_weights_configuration.get(attack_evaluation_weight_column_name, 0))
                result[attack_evaluation_weight_column_name + '-attack-evaluation-weight'].append(attack_evaluation_weight)
        return DataFrame(result)

    def write_store(self, data_type: DataType, data: DataFrame, page_title: str = '') -> None:
        raise Exception('Writing not supported for configuration storage')