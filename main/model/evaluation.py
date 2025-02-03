'''
Classes encapsulating team evaluation logic.
'''
from enum import Enum
from functools import total_ordering
from typing import Any

from pandas import Series

from main.model.library import EnrichedLibraryColumn, LibraryColumn
from main.model.referencedata import PokemonType

class EvaluationColumn(Enum):
    '''
    Attribute of a DataFrame that represents an evaluation model.
    '''
    EVALUATION_NAME = 'evaluation-name'
    # attribute weights
    ATTACK_WEIGHT = 'attack-weight'
    DEFENCE_WEIGHT = 'defence-weight'
    HP_WEIGHT = 'hp-weight'
    ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT = 'attack-cycle-length-inverted-weight'
    ATTACK_CYCLE_DAMAGE_WEIGHT = 'attack-cycle-damage-weight'
    TYPE_VULNERABILITY_WEIGHT = 'type-vulnerability-weight'
    # constraints
    MAX_CP_CONSTRAINT = 'max-cp-constraint'
    # attack evaluation weights
    ATTACK_CYCLE_LENGTH_INVERTED_AE_WEIGHT = 'attack-cycle-length-inverted-attack-evaluation-weight'
    ATTACK_CYCLE_DAMAGE_AE_WEIGHT = 'attack-cycle-damage-attack-evaluation-weight'

def _sum_team_attribute(team: list[dict[str, Any]], attribute: EnrichedLibraryColumn) -> float:
    pokemon_attributes: list[int] = list(map(lambda pokemon: pokemon.get(attribute.value), team))
    return sum(pokemon_attributes)

def _sum_team_attack(team: list[dict[str, Any]]) -> float:
    return _sum_team_attribute(team, EnrichedLibraryColumn.REAL_ATTACK)

def _sum_team_defence(team: list[dict[str, Any]]) -> float:
    return _sum_team_attribute(team, EnrichedLibraryColumn.REAL_DEFENCE)

def _sum_team_hp(team: list[dict[str, Any]]) -> float:
    return _sum_team_attribute(team, EnrichedLibraryColumn.REAL_HP)

def _sum_inverted_attack_cycle_length(team: list[dict[str, Any]]) -> float:
    cycle_lengths: list[int] = list(map(
        lambda pokemon: pokemon.get(EnrichedLibraryColumn.ATTACK_CYCLE_LENGTH.value),
        team))
    inverted_cycle_lengths: list[float] = list(map(lambda cl: 1.0/cl, cycle_lengths))
    return sum(inverted_cycle_lengths)

def _evaluate_max_cp(team: list[dict[str, Any]], constraint: Any) -> bool:
    for pokemon in team:
        if pokemon.get(EnrichedLibraryColumn.CP.value) > constraint:
            return False
    return True

def _sum_attack_cycle_damage(team: list[dict[str, Any]]) -> float:
    return _sum_team_attribute(team, EnrichedLibraryColumn.DPT)

def _sum_type_vuln_across_team(team: list[dict[str, Any]]) -> float:
    result: float = 0.0
    for pokemon_type in PokemonType:
        vulnerable: bool = True
        for pokemon in team:
            if pokemon.get(pokemon_type.value + '_vuln') <= 1.0:
                vulnerable = False
                break
        result -= 1.0 if vulnerable else 0.0
    return result

FEATURE_EVALUATIONS = {
    EvaluationColumn.ATTACK_WEIGHT: _sum_team_attack,
    EvaluationColumn.DEFENCE_WEIGHT: _sum_team_defence,
    EvaluationColumn.HP_WEIGHT: _sum_team_hp,
    EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT: _sum_inverted_attack_cycle_length,
    EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT: _sum_attack_cycle_damage,
    EvaluationColumn.TYPE_VULNERABILITY_WEIGHT: _sum_type_vuln_across_team,
}

CONSTRAINT_EVALUATIONS = {
    EvaluationColumn.MAX_CP_CONSTRAINT: _evaluate_max_cp,
}

ATTACK_FEATURE_EVALUATIONS = {
    EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_AE_WEIGHT:
        _sum_inverted_attack_cycle_length,
    EvaluationColumn.ATTACK_CYCLE_DAMAGE_AE_WEIGHT:
        _sum_attack_cycle_damage,
}

class Evaluation:
    '''
    A class that represents an evaluation model. It evaluates a team of Pokemon
    by extracting values of features from the enriched library and multiplying
    those values by configured weights, and summing the results. If a team
    does not match the configured constraints, it is evaluated to a score of 0.
    '''
    def __init__(self, row: Series) -> None:
        self.evaluation_name = row[EvaluationColumn.EVALUATION_NAME.value]
        self.weights: dict[str, int] = {
            EvaluationColumn.ATTACK_WEIGHT: row.get(EvaluationColumn.ATTACK_WEIGHT.value, 0),
            EvaluationColumn.DEFENCE_WEIGHT: row.get(EvaluationColumn.DEFENCE_WEIGHT.value, 0),
            EvaluationColumn.HP_WEIGHT: row.get(EvaluationColumn.HP_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT: row.get(
                EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT: row.get(
                EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT.value, 0),
            EvaluationColumn.TYPE_VULNERABILITY_WEIGHT: row.get(
                EvaluationColumn.TYPE_VULNERABILITY_WEIGHT.value, 0)
        }
        self.constraints: dict[str, Any] = {
            EvaluationColumn.MAX_CP_CONSTRAINT: row.get(
                EvaluationColumn.MAX_CP_CONSTRAINT.value, None)
        }
        self.attack_evaluation_weights: dict[str, int] = {
            EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_AE_WEIGHT: row.get(
                EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_AE_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_DAMAGE_AE_WEIGHT: row.get(
                EvaluationColumn.ATTACK_CYCLE_DAMAGE_AE_WEIGHT.value, 0)
        }

    def evaluate_team(self, team: list[dict[str, Any]]) -> float:
        '''
        Evaluate the team of the Pokemon by multiplying the evaluation feature
        values by the weights of those features, and summing the results.
        '''
        score = 0
        for feature, weight in self.weights.items():
            score += FEATURE_EVALUATIONS[feature](team) * weight
        return score

    def explain_team(self, team: list[dict[str, Any]]) -> dict[str, float]:
        '''
        Provide a breakdown of the team evaluation in the form of
        the values of evaluation features and their weights.
        '''
        result = {}
        score = 0
        for feature, weight in self.weights.items():
            value: float = FEATURE_EVALUATIONS[feature](team)
            score += value * weight
            result[feature.value.replace('-weight', '')] = {
                'value': value,
                'weight': weight,
            }
        result['score'] = score
        return result

    def matches_constraints(self, team: list[dict[str, Any]]) -> bool:
        '''
        Evaluate whether the team matches the constraint values.
        '''
        for constraint, value in self.constraints.items():
            if not CONSTRAINT_EVALUATIONS[constraint](team, value):
                return False
        return True

    def evaluate_attacks(self, pokemon: dict[str, Any]) -> int:
        '''
        Evaluate the attack combinations of the Pokemon in the team
        by multiplying the attack evaluation feature values by the weights
        of those features, and summing the results.
        '''
        score = 0
        for feature, weight in self.attack_evaluation_weights.items():
            score += ATTACK_FEATURE_EVALUATIONS[feature]([pokemon]) * weight
        return score

@total_ordering
class EvaluationResult:
    '''
    A class that represents the application of an evaluation model
    to a team of Pokemon. This class is sortable by evaluation result.
    '''
    def __init__(self, team: list[dict[str, Any]], e: Evaluation):
        self.team: list[dict[str, Any]] = team
        self.evaluation_name: str = e.evaluation_name
        self.names: list[str] = [pokemon[LibraryColumn.POKEMON_NAME.value] for pokemon in team]
        self.result: float = 0 if not e.matches_constraints(team) else e.evaluate_team(team)

    def __lt__(self, other) -> bool:
        return self.result < other.result

    def __le__(self, other) -> bool:
        if self == other:
            return True
        return self < other

    def __gt__(self, other) -> bool:
        return self.result > other.result

    def __ge__(self, other) -> bool:
        if self == other:
            return True
        return self > other

    def __eq__(self, other) -> bool:
        if not hasattr(other, 'names'):
            return False
        return self.names == other.names

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return self.evaluation_name + '(' + str(self.names) + ') = ' + str(self.result)

    def __repr__(self) -> str:
        return str(self)
