'''
Logic for the 'reduce' step of the calculation process.
'''
import logging
from pandas import concat, DataFrame

from main.core.configuration import configure, ConfigurationService
from main.model.evaluation import EvaluationColumn
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def handler():
    '''
    Pick the top <results-size> teams for each evaluation from the calculated partitions.
    '''
    configure()
    evaluation_data: DataFrame = read_store(DataType.EVALUATION)
    results_size: int = ConfigurationService().get_configuration_property('results-size')
    for evaluation in evaluation_data.to_dict('records'):
        evaluation_name = evaluation[EvaluationColumn.EVALUATION_NAME.value]
        result: DataFrame = DataFrame()
        counter = 0
        while True:
            next_result: DataFrame = read_store(
                DataType.PARTITION_RESULT, evaluation_name + '.' + str(counter))
            if next_result.empty:
                break
            result = concat(
                [result, next_result]).sort_values(
                    by=['result'], ascending=False)[:results_size]
            counter += 1
        write_store(DataType.RESULT, result, evaluation_name)

if __name__ == '__main__':
    handler()
