import logging
from math import ceil, floor
from pandas import DataFrame

from main.core.configuration import configure, ConfigurationService
from main.model.library import LibraryColumn
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_permutations(partitions: list[tuple[int]]) -> list[DataFrame]:
    permutations: list[DataFrame] = []
    for i in range(len(partitions)):
        for j in range(i, len(partitions)):
            for k in range(j, len(partitions)):
                permutations.append(DataFrame({
                    '1': [partitions[i][0], partitions[i][1]],
                    '2': [partitions[j][0], partitions[j][1]],
                    '3': [partitions[k][0], partitions[k][1]]
                }))
    return permutations

def partition(n: int) -> list[tuple[int]]:
    partition_size: int = ConfigurationService().get_configuration_property('partition-size')
    block_size: int = floor(partition_size ** (1./3))
    blocks: list[tuple[int]] = []
    for i in range(0, n, block_size):
        blocks.append((i, min(i + block_size, n) - 1))
    return blocks

def get_delta(library: DataFrame, cache: DataFrame) -> DataFrame:
    if cache.empty:
        logger.info('Cache not found, recalculating whole library')
        return library
    join: DataFrame = library.join(
        cache,
        on=LibraryColumn.POKEMON_NAME.value,
        how='outer',
        lsuffix='_left',
        rsuffix='_right')
    delta: DataFrame = join[
        join[LibraryColumn.POKEMON_LEVEL.value + '_left'] != join[LibraryColumn.POKEMON_LEVEL.value + '_right'] and
        join[LibraryColumn.FAST_ATTACK.value + '_left'] != join[LibraryColumn.FAST_ATTACK.value + '_right'] and
        join[LibraryColumn.CHARGED_ATTACK.value + '_left'] != join[LibraryColumn.CHARGED_ATTACK.value + '_right']
    ]
    logger.info('%d Pokemon changed', delta.size)

def handler() -> int:
    configure()
    library: DataFrame = read_store(DataType.ENRICHED_LIBRARY)
    # cache: DataFrame = read_store(DataType.CACHE)
    # delta: DataFrame = get_delta(library, cache)
    partitions: tuple[list[int]] = partition(len(library))
    permutations: list[DataFrame] = create_permutations(partitions)
    for i in range(len(permutations)):
        write_store(DataType.PARTITION, permutations[i], str(i))
    write_store(DataType.CACHE, library)
    return len(permutations)

if __name__ == '__main__':
    handler()