from enum import Enum
from functools import total_ordering
from pandas import Series
from typing import Any

from main.model.library import EnrichedLibraryColumn, LibraryColumn
from main.model.referencedata import PokemonType

class EvaluationColumn(Enum):
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
    ATTACK_CYCLE_LENGTH_INVERTED_ATTACK_EVALUATION_WEIGHT = 'attack-cycle-length-inverted-attack-evaluation-weight'
    ATTACK_CYCLE_DAMAGE_ATTACK_EVALUATION_WEIGHT = 'attack-cycle-damage-attack-evaluation-weight'

def sum_team_attribute(team: list[dict[str, Any]], attribute: EnrichedLibraryColumn) -> float:
    pokemon_attributes: list[int] = list(map(lambda pokemon: pokemon.get(attribute.value), team))
    return sum(pokemon_attributes)

def sum_team_attack(team: list[dict[str, Any]]) -> float:
    return sum_team_attribute(team, EnrichedLibraryColumn.REAL_ATTACK)

def sum_team_defence(team: list[dict[str, Any]]) -> float:
    return sum_team_attribute(team, EnrichedLibraryColumn.REAL_DEFENCE)

def sum_team_hp(team: list[dict[str, Any]]) -> float:
    return sum_team_attribute(team, EnrichedLibraryColumn.REAL_HP)

def sum_inverted_attack_cycle_length(team: list[dict[str, Any]]) -> float:
    cycle_lengths: list[int] = list(map(lambda pokemon: pokemon.get(EnrichedLibraryColumn.ATTACK_CYCLE_LENGTH.value), team))
    inverted_cycle_lengths: list[float] = list(map(lambda cl: 1.0/cl, cycle_lengths))
    return sum(inverted_cycle_lengths)

def evaluate_max_cp(team: list[dict[str, Any]], constraint: Any) -> bool:
    for pokemon in team:
        if pokemon.get(EnrichedLibraryColumn.CP.value) > constraint:
            return False
    return True

def sum_attack_cycle_damage(team: list[dict[str, Any]]) -> float:
    return sum_team_attribute(team, EnrichedLibraryColumn.DPT)

def sum_type_vuln_across_team(team: list[dict[str, Any]]) -> float:
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
    EvaluationColumn.ATTACK_WEIGHT: sum_team_attack,
    EvaluationColumn.DEFENCE_WEIGHT: sum_team_defence,
    EvaluationColumn.HP_WEIGHT: sum_team_hp,
    EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT: sum_inverted_attack_cycle_length,
    EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT: sum_attack_cycle_damage,
    EvaluationColumn.TYPE_VULNERABILITY_WEIGHT: sum_type_vuln_across_team,
}

CONSTRAINT_EVALUATIONS = {
    EvaluationColumn.MAX_CP_CONSTRAINT: evaluate_max_cp,
}

ATTACK_FEATURE_EVALUATIONS = {
    EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_ATTACK_EVALUATION_WEIGHT: sum_inverted_attack_cycle_length,
    EvaluationColumn.ATTACK_CYCLE_DAMAGE_ATTACK_EVALUATION_WEIGHT: sum_attack_cycle_damage,
}

class Evaluation(object):
    def __init__(self, row: Series) -> None:
        self.evaluation_name = row[EvaluationColumn.EVALUATION_NAME.value]
        self.weights: dict[str, int] = {
            EvaluationColumn.ATTACK_WEIGHT: row.get(EvaluationColumn.ATTACK_WEIGHT.value, 0),
            EvaluationColumn.DEFENCE_WEIGHT: row.get(EvaluationColumn.DEFENCE_WEIGHT.value, 0),
            EvaluationColumn.HP_WEIGHT: row.get(EvaluationColumn.HP_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT: row.get(EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT: row.get(EvaluationColumn.ATTACK_CYCLE_DAMAGE_WEIGHT.value, 0),
            EvaluationColumn.TYPE_VULNERABILITY_WEIGHT: row.get(EvaluationColumn.TYPE_VULNERABILITY_WEIGHT.value, 0)
        }
        self.constraints: dict[str, Any] = {
            EvaluationColumn.MAX_CP_CONSTRAINT: row.get(EvaluationColumn.MAX_CP_CONSTRAINT.value, None)
        }
        self.attack_evaluation_weights: dict[str, int] = {
            EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_ATTACK_EVALUATION_WEIGHT: row.get(EvaluationColumn.ATTACK_CYCLE_LENGTH_INVERTED_ATTACK_EVALUATION_WEIGHT.value, 0),
            EvaluationColumn.ATTACK_CYCLE_DAMAGE_ATTACK_EVALUATION_WEIGHT: row.get(EvaluationColumn.ATTACK_CYCLE_DAMAGE_ATTACK_EVALUATION_WEIGHT.value, 0)
        }

    def evaluate_team(self, team: list[dict[str, Any]]) -> float:
        score = 0
        for feature in self.weights.keys():
            score += FEATURE_EVALUATIONS[feature](team) * self.weights[feature]
        return score

    def explain_team(self, team: list[dict[str, Any]]) -> dict[str, float]:
        result = {}
        score = 0
        for feature in self.weights.keys():
            weight: float = self.weights[feature]
            value: float = FEATURE_EVALUATIONS[feature](team)
            score += value * weight
            result[feature.value.replace('-weight', '')] = {
                'value': value,
                'weight': weight,
            }
        result['score'] = score
        return result

    def matches_constraints(self, team: list[dict[str, Any]]) -> bool:
        for constraint in self.constraints:
            if not CONSTRAINT_EVALUATIONS[constraint](team, self.constraints[constraint]):
                return False
        return True

    def evaluate_attacks(self, pokemon: dict[str, Any]) -> int:
        score = 0
        for feature in self.attack_evaluation_weights.keys():
            score += ATTACK_FEATURE_EVALUATIONS[feature]([pokemon]) * self.attack_evaluation_weights[feature]
        return score

@total_ordering
class EvaluationResult(object):
    def __init__(self, team: list[dict[str, Any]], evaluation: Evaluation):
        self.team: list[dict[str, Any]] = team
        self.evaluation_name: str = evaluation.evaluation_name
        self.names: list[str] = [pokemon[LibraryColumn.POKEMON_NAME.value] for pokemon in team]
        self.result: float = 0 if not evaluation.matches_constraints(team) else evaluation.evaluate_team(team)

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
        return not (self == other)

    def __str__(self) -> str:
        return self.evaluation_name + '(' + str(self.names) + ') = ' + str(self.result)

    def __repr__(self) -> str:
        return str(self)