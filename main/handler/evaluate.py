import datetime
import heapq
import logging
from pandas import DataFrame
from typing import Any

from main.core.configuration import configure, ConfigurationService
from main.core.singleton import Singleton
from main.model.evaluation import Evaluation, EvaluationResult
from main.model.library import LibraryColumn
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ReportingService(Singleton):
    def __init__(self):
        if self.initialised:
            return
        self.progress: int = 0
        self.total: int = 0
        self.initialised = True

    def report_progress(self, progress: int):
        if float(progress - self.progress) / float(self.total) >= 0.1:
            logger.info('Completed %d%% of the calculation', float(progress) / float(self.total) * 100)
            self.progress = progress

def get_pokemon_from_cache(i: int, cache: dict[int, dict[str, Any]], library: DataFrame) -> dict[str, Any]:
    if i not in cache:
        cache[i] = library.iloc[i].to_dict()
    return cache[i]

def handler(event: dict[str, Any], context: dict[str, Any]) -> None:
    configure()
    partition_number: int = event['partition_number']
    partition: DataFrame = read_store(DataType.PARTITION, str(partition_number))
    library: DataFrame = read_store(DataType.ENRICHED_LIBRARY)
    evaluation_data: DataFrame = read_store(DataType.EVALUATION)
    evaluations = []
    results: dict[str, list] = {}
    results_size: int = ConfigurationService().get_configuration_property('results-size')
    for evaluation_data_row in evaluation_data.to_dict('records'):
        evaluation: Evaluation = Evaluation(evaluation_data_row)
        evaluations.append(evaluation)
        results[evaluation.evaluation_name] = []
    n_combinations: int = (partition['1'].values[1] - partition['1'].values[0]) * (partition['2'].values[1] - partition['2'].values[0]) * (partition['2'].values[1] - partition['2'].values[0])
    counter: int = 0
    cache: dict[int, dict[str, Any]] = {}
    start_time: datetime.datetime = datetime.datetime.now()
    logger.info('Evaluating %d formula(e) for %d team combinations', len(evaluations), n_combinations)
    ReportingService().total = n_combinations
    for i in range(partition['1'].values[0], partition['1'].values[1]):
        pokemon1: dict[str, Any] = get_pokemon_from_cache(i, cache, library)
        for j in range(partition['2'].values[0], partition['2'].values[1]):
            if i == j:
                continue
            pokemon2: dict[str, Any] = get_pokemon_from_cache(j, cache, library)
            for k in range(partition['3'].values[0], partition['3'].values[1]):
                if i == k or j == k:
                    continue
                pokemon3: dict[str, Any] = get_pokemon_from_cache(k, cache, library)
                for evaluation in evaluations:
                    evaluation_result: EvaluationResult = EvaluationResult([pokemon1, pokemon2, pokemon3], evaluation)
                    if len(results[evaluation.evaluation_name]) >= results_size:
                        heapq.heapreplace(results[evaluation.evaluation_name], evaluation_result)
                    else:
                        heapq.heappush(results[evaluation.evaluation_name], evaluation_result)
                counter += 1
                ReportingService().report_progress(counter)
    for evaluation_name in results.keys():
        result = DataFrame({
            '1': [r.team[0][LibraryColumn.POKEMON_NAME.value] for r in results[evaluation_name]],
            '2': [r.team[1][LibraryColumn.POKEMON_NAME.value] for r in results[evaluation_name]],
            '3': [r.team[2][LibraryColumn.POKEMON_NAME.value] for r in results[evaluation_name]],
            'result': [r.result for r in results[evaluation_name]]
        })
        write_store(DataType.PARTITION_RESULT, result, evaluation_name + '.' + str(partition_number))
    end_time: datetime.datetime = datetime.datetime.now()
    logger.info('Calculation completed in %s', str(end_time - start_time))

if __name__ == '__main__':
    handler({'partition_number': 3}, {})