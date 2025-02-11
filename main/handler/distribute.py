'''
Logic to distribute the calculation into similarly-sized partitions
that can be mapped by applying an evaluation function onto the subset
of the Pokemon library.
'''
import logging
from math import floor
from pandas import DataFrame

from main.core.configuration import configure, ConfigurationService
from main.model.evaluation import EvaluationColumn
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _create_permutations(partitions: list[tuple[int]]) -> list[DataFrame]:
    permutations: list[DataFrame] = []
    for i, partition_1 in enumerate(partitions):
        for j in range(i, len(partitions)):
            for k in range(j, len(partitions)):
                permutations.append(DataFrame({
                    '1': [partition_1[0], partition_1[1]],
                    '2': [partitions[j][0], partitions[j][1]],
                    '3': [partitions[k][0], partitions[k][1]]
                }))
    return permutations

def _partition(n: int) -> list[tuple[int]]:
    partition_size: int = ConfigurationService().get_configuration_property('partition-size')
    block_size: int = floor(partition_size ** (1./3))
    blocks: list[tuple[int]] = []
    for i in range(0, n, block_size):
        blocks.append((i, min(i + block_size, n) - 1))
    return blocks

def handler() -> int:
    '''
    Partition the calculation load. Each partition is assigned to a specific
    evaluation model, and consists of three segments of the library,
    one for each Pokemon in a team.
    '''
    configure()
    evaluations: DataFrame = read_store(DataType.EVALUATION)
    result = []
    for evaluation_name in evaluations[EvaluationColumn.EVALUATION_NAME.value]:
        library: DataFrame = read_store(DataType.ENRICHED_LIBRARY, page_title=evaluation_name)
        partitions: tuple[list[int]] = _partition(len(library))
        permutations: list[DataFrame] = _create_permutations(partitions)
        for i, permutation in enumerate(permutations):
            permutation_name: str = evaluation_name + '.' + str(i)
            result.append(permutation_name)
            write_store(DataType.PARTITION, permutation, page_title=permutation_name)
    return result

if __name__ == '__main__':
    handler()
