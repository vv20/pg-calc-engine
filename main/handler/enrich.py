'''
Logic to enrich the Pokemon library with reference data and
optimise the Pokemon to score their best in an evaluation.
'''
from collections.abc import Callable
import logging
import numpy
from pandas import concat, DataFrame, Series

from main.core.configuration import configure
from main.model.evaluation import retrieve_evaluations, Evaluation, EvaluationColumn
from main.model.library import EnrichedLibraryColumn, LibraryColumn
from main.model.referencedata import AttackPerPokemonColumn, \
    ChargedAttackColumn, CpmColumn, FastAttackColumn, PokemonEvolutionColumn, \
        PokemonTypeColumn, PokemonType
from main.store import read_store, write_store, DataType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _calculate_cp(lib: DataFrame) -> float:
    max_attack: Series = lib[EnrichedLibraryColumn.MAX_ATTACK.value].astype(int)
    max_defence: Series = lib[EnrichedLibraryColumn.MAX_DEFENCE.value].astype(int)
    max_hp: Series = lib[EnrichedLibraryColumn.MAX_HP.value].astype(int)
    mult: Series = lib[CpmColumn.MULTIPLIER.value].astype(float)
    return numpy.floor(max_attack * numpy.sqrt(max_defence) * numpy.sqrt(max_hp) * (mult ** 2) / 10)

def _enrich_with_pokemon_types(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with Pokemon archtype data')
    pokemon_types: DataFrame = read_store(DataType.POKEMON_TYPE_REFERENCE_DATA)
    return library.merge(pokemon_types, on=PokemonTypeColumn.POKEMON.value, how='left')

def _enrich_with_cp(lib: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with real stats and CP')
    cpm: DataFrame = read_store(DataType.CPM_REFERENCE_DATA)
    cpm[CpmColumn.LEVEL.value] = cpm[CpmColumn.LEVEL.value].transform(float)
    lib[LibraryColumn.POKEMON_LEVEL.value] = lib[LibraryColumn.POKEMON_LEVEL.value].transform(float)
    # in case the CP had been calculated before
    lib.drop(labels=[CpmColumn.MULTIPLIER.value], axis='columns', inplace=True, errors='ignore')
    lib = lib.merge(cpm, on=CpmColumn.LEVEL.value, how='left')
    lib[EnrichedLibraryColumn.MAX_ATTACK.value] = lib[LibraryColumn.ATTACK.value].astype(int) + \
        lib[PokemonTypeColumn.BASE_ATTACK.value].astype(int)
    lib[EnrichedLibraryColumn.REAL_ATTACK.value] = numpy.floor(
        lib[EnrichedLibraryColumn.MAX_ATTACK.value].astype(int) * \
            lib[CpmColumn.MULTIPLIER.value].astype(float))

    lib[EnrichedLibraryColumn.MAX_DEFENCE.value] = lib[LibraryColumn.DEFENCE.value].astype(int) + \
        lib[PokemonTypeColumn.BASE_DEFENCE.value].astype(int)
    lib[EnrichedLibraryColumn.REAL_DEFENCE.value] = numpy.floor(
        lib[EnrichedLibraryColumn.MAX_DEFENCE.value].astype(int) * \
            lib[CpmColumn.MULTIPLIER.value].astype(float))

    lib[EnrichedLibraryColumn.MAX_HP.value] = lib[LibraryColumn.HP.value].astype(int) + \
        lib[PokemonTypeColumn.BASE_HP.value].astype(int)
    lib[EnrichedLibraryColumn.REAL_HP.value] = numpy.floor(
        lib[EnrichedLibraryColumn.MAX_HP.value].astype(int) * \
            lib[CpmColumn.MULTIPLIER.value].astype(float))

    lib[EnrichedLibraryColumn.CP.value] = _calculate_cp(lib)
    return lib

def _stab_calc(attack_type_column: str) -> Callable:
    def _inner(pokemon: Series) -> float:
        if pokemon[PokemonTypeColumn.TYPE_1.value] == pokemon[attack_type_column]:
            return 1.2
        if pokemon[PokemonTypeColumn.TYPE_2.value] == pokemon[attack_type_column]:
            return 1.2
        return 1.0
    return _inner

def _calculate_attack_cycle_length(library: DataFrame, charged_attack: int) -> Series:
    energy_cost_col: EnrichedLibraryColumn = EnrichedLibraryColumn.CHARGED_ATTACK_1_ENERGY_COST
    if charged_attack == 2:
        energy_cost_col = EnrichedLibraryColumn.CHARGED_ATTACK_2_ENERGY_COST
    energy_cost: Series = -library[energy_cost_col.value].astype(float)
    energy_gen: Series = library[FastAttackColumn.ENERGY_GENERATED.value].astype(float)
    fast_attack_len: Series = library[FastAttackColumn.TURNS.value].astype(float)
    return (energy_cost / energy_gen).apply(numpy.ceil) * fast_attack_len

def _calculate_attack_cycle_damage(library: DataFrame, charged_attack: int) -> Series:
    cycle_length: EnrichedLibraryColumn = EnrichedLibraryColumn.ATTACK_CYCLE_1_LENGTH
    damage: EnrichedLibraryColumn = EnrichedLibraryColumn.CHARGED_ATTACK_1_DAMAGE
    stab: EnrichedLibraryColumn = EnrichedLibraryColumn.CHARGED_ATTACK_1_STAB
    if charged_attack == 2:
        cycle_length = EnrichedLibraryColumn.ATTACK_CYCLE_2_LENGTH
        damage = EnrichedLibraryColumn.CHARGED_ATTACK_2_DAMAGE
        stab = EnrichedLibraryColumn.CHARGED_ATTACK_2_STAB
    attack_cycle_len: Series = library[cycle_length.value]
    fast_attack_len: Series = library[FastAttackColumn.TURNS.value].astype(float)
    fast_attack_dmg: Series = library[FastAttackColumn.DAMAGE.value].astype(float)
    fast_attack_stab: Series = library[EnrichedLibraryColumn.FAST_ATTACK_STAB.value].astype(float)
    charged_attack_dmg: Series = library[damage.value].astype(float)
    charged_attack_stab: Series = library[stab.value].astype(float)
    return attack_cycle_len / fast_attack_len * (fast_attack_dmg * fast_attack_stab) + \
            (charged_attack_dmg * charged_attack_stab)

def _calculate_damage_per_turn(library: DataFrame, charged_attack: int) -> Series:
    cycle_length: EnrichedLibraryColumn = EnrichedLibraryColumn.ATTACK_CYCLE_1_LENGTH
    cycle_damage: EnrichedLibraryColumn = EnrichedLibraryColumn.ATTACK_CYCLE_1_DAMAGE
    if charged_attack == 2:
        cycle_length: EnrichedLibraryColumn = EnrichedLibraryColumn.ATTACK_CYCLE_2_LENGTH
        cycle_damage: EnrichedLibraryColumn = EnrichedLibraryColumn.ATTACK_CYCLE_2_DAMAGE
    acd: Series = library[cycle_damage.value]
    acl: Series = library[cycle_length.value]
    return acd / acl

def _enrich_with_attacks(lib: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with attack data')
    fast_attacks: DataFrame = read_store(DataType.FAST_ATTACK_REFERENCE_DATA)
    charged_attacks: DataFrame = read_store(DataType.CHARGED_ATTACK_REFERENCE_DATA)
    # enrich with reference data
    lib = lib.merge(
        fast_attacks,
        left_on=LibraryColumn.FAST_ATTACK.value,
        right_on=FastAttackColumn.ATTACK.value)
    lib = lib.merge(
        charged_attacks,
        left_on=LibraryColumn.CHARGED_ATTACK_1.value,
        right_on=ChargedAttackColumn.ATTACK.value)
    lib.rename(
        columns={
            ChargedAttackColumn.DAMAGE.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_1_DAMAGE.value,
            ChargedAttackColumn.TYPE.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_1_TYPE.value,
            ChargedAttackColumn.ENERGY_COST.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_1_ENERGY_COST.value
        }, inplace=True)
    lib.drop(columns=[ChargedAttackColumn.ATTACK.value], inplace=True)
    lib = lib.merge(
        charged_attacks,
        left_on=LibraryColumn.CHARGED_ATTACK_2.value,
        right_on=ChargedAttackColumn.ATTACK.value)
    lib.rename(
        columns={
            ChargedAttackColumn.DAMAGE.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_2_DAMAGE.value,
            ChargedAttackColumn.TYPE.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_2_TYPE.value,
            ChargedAttackColumn.ENERGY_COST.value: \
                EnrichedLibraryColumn.CHARGED_ATTACK_2_ENERGY_COST.value
        }, inplace=True)
    lib.drop(columns=[ChargedAttackColumn.ATTACK.value], inplace=True)
    # calculate derived data
    lib[EnrichedLibraryColumn.FAST_ATTACK_STAB.value] = lib.apply(
        _stab_calc(FastAttackColumn.TYPE.value), axis='columns')
    lib[EnrichedLibraryColumn.CHARGED_ATTACK_1_STAB.value] = lib.apply(
        _stab_calc(EnrichedLibraryColumn.CHARGED_ATTACK_1_TYPE.value), axis='columns')
    lib[EnrichedLibraryColumn.CHARGED_ATTACK_2_STAB.value] = lib.apply(
        _stab_calc(EnrichedLibraryColumn.CHARGED_ATTACK_2_TYPE.value), axis='columns')
    lib[EnrichedLibraryColumn.ATTACK_CYCLE_1_LENGTH.value] = _calculate_attack_cycle_length(lib, 1)
    lib[EnrichedLibraryColumn.ATTACK_CYCLE_1_DAMAGE.value] = _calculate_attack_cycle_damage(lib, 1)
    lib[EnrichedLibraryColumn.DPT_1.value] = _calculate_damage_per_turn(lib, 1)
    lib[EnrichedLibraryColumn.ATTACK_CYCLE_2_LENGTH.value] = _calculate_attack_cycle_length(lib, 2)
    lib[EnrichedLibraryColumn.ATTACK_CYCLE_2_DAMAGE.value] = _calculate_attack_cycle_damage(lib, 2)
    lib[EnrichedLibraryColumn.DPT_2.value] = _calculate_damage_per_turn(lib, 2)
    return lib

def _calculate_type_vulnerability(type_chart_slice: Series) -> Callable:
    def _inner(row: Series) -> float:
        type1: str = row.get(PokemonTypeColumn.TYPE_1.value)
        type2: str = row.get(PokemonTypeColumn.TYPE_2.value)
        vuln1: float = type_chart_slice[type1].astype(float).sum()
        vuln2: float = 1.0
        if type2 is not None and type2 is not numpy.nan:
            vuln2 = type_chart_slice[type2].astype(float).sum()
        return vuln1 * vuln2
    return _inner

def _calculate_type_strength(type_chart_slice: Series) -> Callable:
    def _inner(row: Series) -> float:
        type1: str = row.get(EnrichedLibraryColumn.CHARGED_ATTACK_1_TYPE.value)
        type2: str = row.get(EnrichedLibraryColumn.CHARGED_ATTACK_2_TYPE.value)
        str1: float = float(type_chart_slice[type1])
        str2: float = 1.0
        if type2 is not None and type2 is not numpy.nan:
            str2 = float(type_chart_slice[type2])
        return str1 * str2
    return _inner

def _enrich_with_type_vulnerabilities(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with type vulnerability data')
    type_chart: DataFrame = read_store(DataType.TYPE_CHART_REFERENCE_DATA)
    for pokemon_type in PokemonType:
        # take the type chart row to check which types the pokemon is vulnerable to
        type_chart_slice: Series = type_chart[type_chart['Type'] == pokemon_type.value]
        result = library.apply(_calculate_type_vulnerability(type_chart_slice), axis='columns')
        library[pokemon_type.value + '_vuln'] = result
    return library

def _enrich_with_type_strength(library: DataFrame) -> DataFrame:
    logger.info('Enriching the Pokemon library with type vulnerability data')
    type_chart: DataFrame = read_store(DataType.TYPE_CHART_REFERENCE_DATA)
    for pokemon_type in PokemonType:
        # take the type chart column to check which types the pokemon is strong against
        type_chart_slice: Series = type_chart[pokemon_type.value]
        type_chart_slice.index = type_chart['Type']
        result = library.apply(_calculate_type_strength(type_chart_slice), axis='columns')
        library[pokemon_type.value + '_str'] = result
    return library

def _expand_evolutions(library: DataFrame) -> DataFrame:
    evolved: DataFrame = DataFrame(columns=library.columns)
    evol_iter: DataFrame = library
    evolutions: DataFrame = read_store(DataType.EVOLUTION)
    while len(evol_iter) > 0:
        evolved = concat([evolved, evol_iter])
        evol_iter = evol_iter.merge(
            evolutions,
            how='inner',
            left_on=LibraryColumn.POKEMON_TYPE.value,
            right_on=PokemonEvolutionColumn.POKEMON.value)
        evol_iter.drop(labels=[LibraryColumn.POKEMON_TYPE.value], axis='columns', inplace=True)
        evol_iter.rename(
            columns={
                PokemonEvolutionColumn.EVOLUTION.value: LibraryColumn.POKEMON_TYPE.value
            }, inplace=True)
    evolved[LibraryColumn.POKEMON_NAME.value] += ' as '
    evolved[LibraryColumn.POKEMON_NAME.value] += evolved[LibraryColumn.POKEMON_TYPE.value]
    return evolved.reset_index(drop=True)

def _filter_with_constraints(library: DataFrame, evaluation: Evaluation) -> DataFrame:
    filtered = _enrich_with_pokemon_types(library)
    filtered = _enrich_with_cp(filtered)
    filtered = filtered[filtered.apply(evaluation.matches_constraints, axis='columns')]
    return filtered.reset_index(drop=True)

def _maximise_level(lib: DataFrame, evaluation: Evaluation) -> DataFrame:
    if not EvaluationColumn.MAX_CP_CONSTRAINT in evaluation.constraints:
        lib[LibraryColumn.POKEMON_LEVEL.value] = Series(numpy.array([50] * len(lib)))
        return _enrich_with_cp(lib)
    max_cp: int = evaluation.constraints[EvaluationColumn.MAX_CP_CONSTRAINT]
    max_attack: Series = lib[EnrichedLibraryColumn.MAX_ATTACK.value]
    max_defence: Series = numpy.sqrt(lib[EnrichedLibraryColumn.MAX_DEFENCE.value])
    max_hp: Series = numpy.sqrt(lib[EnrichedLibraryColumn.MAX_HP.value])
    max_cpm: Series = numpy.sqrt(max_cp * 10 / max_attack / max_defence / max_hp)
    levels: Series = Series(numpy.array([0.5] * len(lib)))
    cpm: DataFrame = read_store(DataType.CPM_REFERENCE_DATA)
    for _, level in cpm.iterrows():
        levels[max_cpm > float(level[CpmColumn.MULTIPLIER.value])] += 0.5
    lib[LibraryColumn.POKEMON_LEVEL.value] = levels
    lib[LibraryColumn.POKEMON_NAME.value] += ' at level '
    lib[LibraryColumn.POKEMON_NAME.value] += lib[LibraryColumn.POKEMON_LEVEL.value].transform(str)
    # re-calculate CP with the new levels
    return _enrich_with_cp(lib).reset_index(drop=True)

def _optimise_attacks(library: DataFrame, evaluation: Evaluation) -> DataFrame:
    fast_attacks: DataFrame = read_store(DataType.FAST_ATTACK_PER_POKEMON_REFERENCE_DATA)
    charged_attacks: DataFrame = read_store(DataType.CHARGED_ATTACK_PER_POKEMON_REFERENCE_DATA)
    library.drop(
        labels=[LibraryColumn.FAST_ATTACK.value, LibraryColumn.CHARGED_ATTACK_1.value],
        axis='columns',
        inplace=True,
        errors='ignore')
    library = library.merge(
        fast_attacks,
        how='inner',
        left_on=LibraryColumn.POKEMON_TYPE.value,
        right_on=AttackPerPokemonColumn.POKEMON.value)
    library.rename(
        columns={
            AttackPerPokemonColumn.ATTACK.value: LibraryColumn.FAST_ATTACK.value
        }, inplace=True)
    library = library.merge(
        charged_attacks,
        how='inner',
        left_on=LibraryColumn.POKEMON_TYPE.value,
        right_on=AttackPerPokemonColumn.POKEMON.value)
    library.rename(
        columns={
            AttackPerPokemonColumn.ATTACK.value: LibraryColumn.CHARGED_ATTACK_1.value,
        }, inplace=True)
    library = library.merge(
        charged_attacks,
        how='inner',
        left_on=LibraryColumn.POKEMON_TYPE.value,
        right_on=AttackPerPokemonColumn.POKEMON.value)
    library.rename(
        columns={
            AttackPerPokemonColumn.ATTACK.value: LibraryColumn.CHARGED_ATTACK_2.value,
        }, inplace=True)
    library = library[library[LibraryColumn.CHARGED_ATTACK_1.value] != \
                      library[LibraryColumn.CHARGED_ATTACK_2.value]].reset_index(drop=True)
    library = _enrich_with_attacks(library)
    library = _enrich_with_type_strength(library)
    library['attack_eval'] = library.apply(evaluation.evaluate_attacks, axis='columns')
    group = library.groupby([LibraryColumn.POKEMON_NAME.value, LibraryColumn.POKEMON_TYPE.value])
    best_attacks = group['attack_eval'].transform(max)
    library = library[library['attack_eval'] == best_attacks].drop(columns=['attack_eval'])
    library[LibraryColumn.POKEMON_NAME.value] += ' with fast attack '
    library[LibraryColumn.POKEMON_NAME.value] += library[LibraryColumn.FAST_ATTACK.value]
    library[LibraryColumn.POKEMON_NAME.value] += ' and first charged attack '
    library[LibraryColumn.POKEMON_NAME.value] += library[LibraryColumn.CHARGED_ATTACK_1.value]
    library[LibraryColumn.POKEMON_NAME.value] += ' and second charged attack '
    library[LibraryColumn.POKEMON_NAME.value] += library[LibraryColumn.CHARGED_ATTACK_2.value]
    return library

def _optimise(library: DataFrame, evaluation: Evaluation) -> DataFrame:
    logger.info('Optimising Pokemon for the %s evaluation', evaluation.evaluation_name)
    library = _expand_evolutions(library)
    library = _filter_with_constraints(library, evaluation)
    library = _maximise_level(library, evaluation)
    library = _optimise_attacks(library, evaluation)
    library = _enrich_with_type_vulnerabilities(library)
    return library

def handler() -> None:
    '''
    Enrich the library of Pokemon with reference data and produce copies of
    the enriched library in which the Pokemon are optimised to be their
    best versions for the evaluation formula.
    '''
    configure()
    library: DataFrame = read_store(DataType.LIBRARY)
    evaluations: list[Evaluation] = retrieve_evaluations(read_store(DataType.EVALUATION))
    for evaluation in evaluations:
        optimised_library = _optimise(library, evaluation)
        write_store(
            DataType.ENRICHED_LIBRARY,
            optimised_library,
            page_title=evaluation.evaluation_name)

if __name__ == '__main__':
    handler()
