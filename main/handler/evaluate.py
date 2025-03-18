'''
Logic to evaluate a partition of the Pokemon library according to
an evaluation formula.
'''
from typing import Any

import datetime
import heapq
import logging
from pandas import DataFrame

from main.core.configuration import configure, ConfigurationService
from main.core.singleton import Singleton
from main.model.evaluation import retrieve_evaluations, Evaluation, EvaluationResult
from main.model.library import LibraryColumn
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ReportingService(Singleton):
    '''
    A service that is used to report the progress of a calculation.
    '''
    def __init__(self):
        if self.initialised:
            return
        self.progress: int = 0
        self.total: int = 0
        self.counter: int = 0
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.initialised = True

    def report_progress(self) -> None:
        '''
        Report the current progress of a calculation.
        '''
        self.counter += 1
        if float(self.counter - self.progress) / float(self.total) >= 0.1:
            logger.info('Completed %d%% of the calculation',
                        float(self.counter) / float(self.total) * 100)
            self.progress = self.counter

    def prepare(self, partition: DataFrame, evaluation_name: str) -> None:
        '''
        Prepare to report the progress of a calculation.
        '''
        partition_1_len: int = partition['1'].values[1] - partition['1'].values[0]
        partition_2_len: int = partition['2'].values[1] - partition['2'].values[0]
        partition_3_len: int = partition['3'].values[1] - partition['3'].values[0]
        self.total = partition_1_len * partition_2_len * partition_3_len
        logger.info('Evaluating formula %s for %d team combinations', evaluation_name, self.total)

    def start(self) -> None:
        '''
        Report the start of a calculation.
        '''
        self.start_time = datetime.datetime.now()
        self.counter = 0
        self.progress = 0

    def end(self) -> None:
        '''
        Report the end of the calculation.
        '''
        self.end_time = datetime.datetime.now()
        logger.info('Calculation completed in %s', str(self.end_time - self.start_time))

_cache: dict[int, dict[str, Any]] = {}
def _get_pokemon_from_cache(i: int, library: DataFrame) -> dict[str, Any]:
    if i not in _cache:
        _cache[i] = library.iloc[i].to_dict()
    return _cache[i]

def handler(event: dict[str, Any], context: dict[str, Any]) -> None:
    '''
    Apply the evaluation formula to all teams in the partition, and return
    the top <results-size> results by evaluation score.
    '''
    configure()
    evaluation_name: str = event['permutation'].split('.')[0]
    partition: DataFrame = read_store(DataType.PARTITION, page_title=event['permutation'])
    library: DataFrame = read_store(DataType.ENRICHED_LIBRARY, page_title=evaluation_name)
    results_size: int = ConfigurationService().get_configuration_property('results-size')
    result: list = []
    evaluation: Evaluation = [e for e in retrieve_evaluations(
        read_store(DataType.EVALUATION)) if e.evaluation_name == evaluation_name][0]
    ReportingService().prepare(partition, evaluation_name)
    ReportingService().start()
    for i in range(partition['1'].values[0], partition['1'].values[1]):
        pokemon1: dict[str, Any] = _get_pokemon_from_cache(i, library)
        for j in range(partition['2'].values[0], partition['2'].values[1]):
            if i == j:
                continue
            pokemon2: dict[str, Any] = _get_pokemon_from_cache(j, library)
            for k in range(partition['3'].values[0], partition['3'].values[1]):
                if k in (i, j):
                    continue
                pokemon3: dict[str, Any] = _get_pokemon_from_cache(k, library)
                evaluation_result: EvaluationResult = EvaluationResult(
                    [pokemon1, pokemon2, pokemon3],
                    evaluation)
                if len(result) >= results_size:
                    heapq.heapreplace(result, evaluation_result)
                else:
                    heapq.heappush(result, evaluation_result)
                ReportingService().report_progress()
    write_store(
        DataType.PARTITION_RESULT,
        DataFrame({
                '1': [r.team[0][LibraryColumn.POKEMON_NAME.value] for r in result],
                '2': [r.team[1][LibraryColumn.POKEMON_NAME.value] for r in result],
                '3': [r.team[2][LibraryColumn.POKEMON_NAME.value] for r in result],
                'result': [r.result for r in result]
            }),
        page_title=event['permutation'])
    ReportingService().end()

if __name__ == '__main__':
    handler({'permutation': 'my-first-gl-evaluation.0'}, {})
