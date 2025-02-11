from main.model.evaluation import Evaluation, EvaluationColumn, EvaluationResult, retrieve_evaluations
from main.store import read_store, DataType

from test.util import framework_setup

IVYSAUR = {
    'Name': 'Ivysaur',
    'Pokemon': 'Ivysaur',
    'Fast attack': 'Vine Whip',
    'Charged attack 1': 'Sludge Bomb',
    'Level': 20,
    'IV attack': 14,
    'IV defence': 10,
    'IV HP': 13,
    'Number': 2,
    'Base attack': 151,
    'Base defence': 143,
    'Base HP': 155,
    'Type 1': 'Grass',
    'Type 2': 'Poison',
    'Multiplier': 0.5974,
    'Max attack': 165,
    'Real attack': 98.0,
    'Max defence': 153,
    'Real defence': 91.0,
    'Max HP': 168,
    'Real HP': 100.0,
    'CP': 944.0,
    'Fast attack type': 'Grass',
    'Fast attack duration': 2,
    'Fast attack damage': 5,
    'Fast attack energy generated': 8,
    'Charged attack type': 'Poison',
    'Charged attack damage': 80,
    'Charged attack energy cost': -50,
    'Fast attack STAB': 1.2,
    'Charged attack STAB': 1.2,
    'Attack cycle length': 13.0,
    'Attack cycle damage': 112.5,
    'DPT': 8.653846153846153,
    'Normal_vuln': 1.0,
    'Fire_vuln': 1.25,
    'Water_vuln': 0.8,
    'Grass_vuln': 0.6400000000000001,
    'Electric_vuln': 0.8,
    'Ice_vuln': 1.25,
    'Fighting_vuln': 0.8,
    'Poison_vuln': 1.0,
    'Ground_vuln': 1.0,
    'Flying_vuln': 1.25,
    'Psychic_vuln': 1.25,
    'Bug_vuln': 1.0,
    'Rock_vuln': 1.0,
    'Ghost_vuln': 1.0,
    'Dragon_vuln': 1.0,
    'Dark_vuln': 1.0,
    'Steel_vuln': 1.0,
    'Fairy_vuln': 0.8,
}

CHARMANDER = {
    'Name': 'Charmander',
    'Pokemon': 'Charmander',
    'Fast attack': 'Scratch',
    'Charged attack 1': 'Flame Charge',
    'Level': 20,
    'IV attack': 13,
    'IV defence': 14,
    'IV HP': 15,
    'Number': 4,
    'Base attack': 116,
    'Base defence': 93,
    'Base HP': 118,
    'Type 1': 'Fire',
    'Type 2': '',
    'Multiplier': 0.5974,
    'Max attack': 129,
    'Real attack': 77.0,
    'Max defence': 107,
    'Real defence': 63.0,
    'Max HP': 133,
    'Real HP': 79.0,
    'CP': 549.0,
    'Fast attack type': 'Normal',
    'Fast attack duration': 1,
    'Fast attack damage': 4,
    'Fast attack energy generated': 2,
    'Charged attack type': 'Fire',
    'Charged attack damage': 65,
    'Charged attack energy cost': -50,
    'Fast attack STAB': 1.0,
    'Charged attack STAB': 1.2,
    'Attack cycle length': 25.0,
    'Attack cycle damage': 165.0,
    'DPT': 6.6,
    'Normal_vuln': 1.0,
    'Fire_vuln': 0.8,
    'Water_vuln': 1.25,
    'Grass_vuln': 0.8,
    'Electric_vuln': 1.0,
    'Ice_vuln': 0.8,
    'Fighting_vuln': 1.0,
    'Poison_vuln': 1.0,
    'Ground_vuln': 1.25,
    'Flying_vuln': 1.0,
    'Psychic_vuln': 1.0,
    'Bug_vuln': 0.8,
    'Rock_vuln': 1.25,
    'Ghost_vuln': 1.0,
    'Dragon_vuln': 1.0,
    'Dark_vuln': 1.0,
    'Steel_vuln': 0.8,
    'Fairy_vuln': 0.8,
}

BUTTERFREE = {
    'Name': 'Butterfree',
    'Pokemon': 'Butterfree',
    'Fast attack': 'Confusion',
    'Charged attack 1': 'Psychic',
    'Level': 19,
    'IV attack': 15,
    'IV defence': 10,
    'IV HP': 15,
    'Number': 12,
    'Base attack': 167,
    'Base defence': 137,
    'Base HP': 155,
    'Type 1': 'Bug',
    'Type 2': 'Flying',
    'Multiplier': 0.5822789,
    'Max attack': 182,
    'Real attack': 105.0,
    'Max defence': 147,
    'Real defence': 85.0,
    'Max HP': 170,
    'Real HP': 98.0,
    'CP': 975.0,
    'Fast attack type': 'Psychic',
    'Fast attack duration': 4,
    'Fast attack damage': 16,
    'Fast attack energy generated': 12,
    'Charged attack type': 'Psychic',
    'Charged attack damage': 75,
    'Charged attack energy cost': -55,
    'Fast attack STAB': 1.0,
    'Charged attack STAB': 1.0,
    'Attack cycle length': 19.0,
    'Attack cycle damage': 151.0,
    'DPT': 7.947368421052632,
    'Normal_vuln': 1.0,
    'Fire_vuln': 1.25,
    'Water_vuln': 1.0,
    'Grass_vuln': 0.6400000000000001,
    'Electric_vuln': 1.25,
    'Ice_vuln': 1.25,
    'Fighting_vuln': 0.6400000000000001,
    'Poison_vuln': 1.0,
    'Ground_vuln': 0.6400000000000001,
    'Flying_vuln': 1.25,
    'Psychic_vuln': 1.0,
    'Bug_vuln': 0.8,
    'Rock_vuln': 1.5625,
    'Ghost_vuln': 1.0,
    'Dragon_vuln': 1.0,
    'Dark_vuln': 1.0,
    'Steel_vuln': 1.0,
    'Fairy_vuln': 1.0,
}

def test_evaluation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.evaluate_team([IVYSAUR, CHARMANDER, BUTTERFREE]) == 1282.3441295546559

def test_explanation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    explanation = evaluation.explain_team([IVYSAUR, CHARMANDER, BUTTERFREE])
    expected_explanation = {
        'attack': {
            'value': 280.0,
            'weight': 1
        },
        'attack-cycle-damage': {
            'value': 23.201214574898785,
            'weight': 10
        },
        'attack-cycle-length-inverted': {
            'value': 0.16955465587044535,
            'weight': 1500
        },
        'defence': {
            'value': 239.0,
            'weight': 1
        },
        'hp': {
            'value': 277.0,
            'weight': 1
        },
        'score': 1282.3441295546559,
        'type-vulnerability': {
            'value': 0.0,
            'weight': 100
        }
    }
    assert explanation == expected_explanation

def test_constraint_matching(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.matches_constraints(CHARMANDER)
    assert not evaluation.matches_constraints(BUTTERFREE)

def test_attack_evaluation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.evaluate_attacks(IVYSAUR) == 16.346153846153847

def test_compare_evaluation_results(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    result1 = EvaluationResult(team=[IVYSAUR, CHARMANDER, BUTTERFREE], e=evaluation)
    evaluation.constraints[EvaluationColumn.MAX_CP_CONSTRAINT] = 1500
    result2 = EvaluationResult(team=[CHARMANDER, IVYSAUR, BUTTERFREE], e=evaluation)

    assert result1 < result2
    assert result1 <= result2
    assert result2 <= result2
    assert result2 > result1
    assert result2 >= result1
    assert result2 >= result2
    assert result1 == result1
    assert result1 != {}
    assert result1 != result2
    assert repr(result1) == 'test-evaluation([\'Ivysaur\', \'Charmander\', \'Butterfree\']) = 0'