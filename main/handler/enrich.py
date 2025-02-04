import logging
import numpy
from pandas import DataFrame, Series

from main.core.configuration import configure
from main.model.evaluation import retrieve_evaluations, Evaluation
from main.model.library import EnrichedLibraryColumn, LibraryColumn
from main.model.referencedata import ChargedAttackColumn, CpmColumn, FastAttackColumn, PokemonTypeColumn, PokemonType
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def enrich_with_pokemon_types(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with Pokemon archtype data')
    pokemon_types: DataFrame = read_store(DataType.POKEMON_TYPE_REFERENCE_DATA)
    return library.merge(pokemon_types, on=PokemonTypeColumn.POKEMON.value, how='left')

def enrich_with_cpm(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with real stats and CP')
    cpm: DataFrame = read_store(DataType.CPM_REFERENCE_DATA)
    library = library.merge(cpm, on=CpmColumn.LEVEL.value, how='left')
    library[EnrichedLibraryColumn.MAX_ATTACK.value] = library[LibraryColumn.ATTACK.value].astype(int) + library[PokemonTypeColumn.BASE_ATTACK.value].astype(int)
    library[EnrichedLibraryColumn.REAL_ATTACK.value] = (library[EnrichedLibraryColumn.MAX_ATTACK.value] * library[CpmColumn.MULTIPLIER.value].astype(float)).apply(numpy.floor)
    library[EnrichedLibraryColumn.MAX_DEFENCE.value] = library[LibraryColumn.DEFENCE.value].astype(int) + library[PokemonTypeColumn.BASE_DEFENCE.value].astype(int)
    library[EnrichedLibraryColumn.REAL_DEFENCE.value] = (library[EnrichedLibraryColumn.MAX_DEFENCE.value] * library[CpmColumn.MULTIPLIER.value].astype(float)).apply(numpy.floor)
    library[EnrichedLibraryColumn.MAX_HP.value] = library[LibraryColumn.HP.value].astype(int) + library[PokemonTypeColumn.BASE_HP.value].astype(int)
    library[EnrichedLibraryColumn.REAL_HP.value] = (library[EnrichedLibraryColumn.MAX_HP.value] * library[CpmColumn.MULTIPLIER.value].astype(float)).apply(numpy.floor)
    library[EnrichedLibraryColumn.CP.value] = (library[EnrichedLibraryColumn.MAX_ATTACK.value] * library[EnrichedLibraryColumn.MAX_DEFENCE.value].apply(numpy.sqrt) * library[EnrichedLibraryColumn.MAX_HP.value].apply(numpy.sqrt) * pow(library[CpmColumn.MULTIPLIER.value].astype(float), 2)).floordiv(10)
    return library

def enrich_with_attacks(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with attack data')
    fast_attacks: DataFrame = read_store(DataType.FAST_ATTACK_REFERENCE_DATA)
    charged_attacks: DataFrame = read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    library = library.merge(fast_attacks, left_on=LibraryColumn.FAST_ATTACK.value, right_on=FastAttackColumn.ATTACK.value)
    library = library.merge(charged_attacks, left_on=LibraryColumn.CHARGED_ATTACK.value, right_on=ChargedAttackColumn.ATTACK.value)
    library[EnrichedLibraryColumn.FAST_ATTACK_STAB.value] = library.apply(lambda pokemon: 1.2 if pokemon[PokemonTypeColumn.TYPE_1.value] == pokemon[FastAttackColumn.TYPE.value] or pokemon[PokemonTypeColumn.TYPE_2.value] == pokemon[FastAttackColumn.TYPE.value] else 1.0, axis='columns')
    library[EnrichedLibraryColumn.CHARGED_ATTACK_STAB.value] = library.apply(lambda pokemon: 1.2 if pokemon[PokemonTypeColumn.TYPE_1.value] == pokemon[ChargedAttackColumn.TYPE.value] or pokemon[PokemonTypeColumn.TYPE_2.value] == pokemon[ChargedAttackColumn.TYPE.value] else 1.0, axis='columns')
    library[EnrichedLibraryColumn.ATTACK_CYCLE_LENGTH.value] = ((-library[ChargedAttackColumn.ENERGY_COST.value].astype(float)) / library[FastAttackColumn.ENERGY_GENERATED.value].astype(float) * library[FastAttackColumn.TURNS.value].astype(float)).apply(numpy.ceil)
    library[EnrichedLibraryColumn.ATTACK_CYCLE_DAMAGE.value] = library[EnrichedLibraryColumn.ATTACK_CYCLE_LENGTH.value].astype(float) / library[FastAttackColumn.TURNS.value].astype(float) * library[FastAttackColumn.DAMAGE.value].astype(float) + library[ChargedAttackColumn.DAMAGE.value].astype(float)
    library[EnrichedLibraryColumn.DPT.value] = library[EnrichedLibraryColumn.ATTACK_CYCLE_DAMAGE.value] / library[EnrichedLibraryColumn.ATTACK_CYCLE_LENGTH.value]
    return library

def enrich_with_type_vulnerabilities(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with type vulnerability data')
    type_chart: DataFrame = read_store(DataType.TYPE_CHART_REFERENCE_DATA)
    for pokemon_type in PokemonType:
        def calculate_type_vulnerability(row: Series):
            type1: str = row.get(PokemonTypeColumn.TYPE_1.value)
            type2: str = row.get(PokemonTypeColumn.TYPE_2.value)
            vuln1: float = type_chart[type_chart['Type'] == pokemon_type.value][type1].astype(float).sum()
            vuln2: float = 1.0
            if type2 is not None and type2 is not numpy.nan:
                vuln2 = type_chart[type_chart['Type'] == pokemon_type.value][type2].astype(float).sum()
            return vuln1 * vuln2
        result = library.apply(calculate_type_vulnerability, axis='columns')
        library[pokemon_type.value + '_vuln'] = result
    return library

def optimise(library: DataFrame, evaluation: Evaluation) -> DataFrame:
    logger.info('Optimising Pokemon for the %s evaluation', evaluation.evaluation_name)
    return library

def enrich(library: DataFrame) -> DataFrame:
    enriched_library = enrich_with_pokemon_types(library)
    enriched_library = enrich_with_cpm(enriched_library)
    enriched_library = enrich_with_attacks(enriched_library)
    return enrich_with_type_vulnerabilities(enriched_library)

def handler() -> None:
    configure()
    library: DataFrame = read_store(DataType.LIBRARY)
    enriched_library: DataFrame = enrich(library)
    write_store(DataType.ENRICHED_LIBRARY, enriched_library)
    evaluations: list[Evaluation] = retrieve_evaluations(read_store(DataType.EVALUATION))
    for evaluation in evaluations:
        optimised_library = optimise(enriched_library, evaluation)
        write_store(DataType.ENRICHED_LIBRARY, optimised_library, page_title=evaluation.evaluation_name)

if __name__ == '__main__':
    handler()