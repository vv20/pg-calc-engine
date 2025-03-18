from main.model.evaluation import EvaluationColumn, EvaluationResult, retrieve_evaluations
from main.store import read_store, DataType

from test.util import framework_setup

IVYSAUR = {
    'Name': 'Ivysaur',
    'Pokemon': 'Ivysaur',
    'Level': 33.5,
    'IV attack': 14,
    'IV defence': 10,
    'IV HP': 13,
    'Number': 2,
    'Base attack': 151,
    'Base defence': 143,
    'Base HP': 155,
    'Type 1': 'Grass',
    'Type 2': 'Poison',
    'Max attack': 165,
    'Real attack': 124,
    'Max defence': 153,
    'Real defence': 115,
    'Max HP': 168,
    'Real HP': 126,
    'CP': 1498,
    'Multiplier': 0.7527290867,
    'Fast attack': 'Vine Whip',
    'Charged attack 1': 'Power Whip',
    'Charged attack 2': 'Sludge Bomb',
    'Fast attack type': 'Grass',
    'Fast attack duration': 2,
    'Fast attack damage': 5,
    'Fast attack energy generated': 8,
    'Charged attack 1 type': 'Grass',
    'Charged attack 1 damage': 90,
    'Charged attack 1 energy cost': -50,
    'Charged attack 2 type': 'Poison',
    'Charged attack 2 damage': 80,
    'Charged attack 2 energy cost': -50,
    'Fast attack STAB': 1.2,
    'Charged attack 1 STAB': 1.2,
    'Charged attack 2 STAB': 1.2,
    'Attack cycle 1 length': 14,
    'Attack cycle 1 damage': 150,
    'DPT 1': 10.7142857142857,
    'Attack cycle 2 length': 14,
    'Attack cycle 2 damage': 138,
    'DPT 2': 9.85714285714286,
    'Normal_str': 1,
    'Fire_str': 0.8,
    'Water_str': 1.25,
    'Grass_str': 1,
    'Electric_str': 1,
    'Ice_str': 1,
    'Fighting_str': 1,
    'Poison_str': 0.64,
    'Ground_str': 1,
    'Flying_str': 0.8,
    'Psychic_str': 1,
    'Bug_str': 0.8,
    'Rock_str': 1,
    'Ghost_str': 0.8,
    'Dragon_str': 0.8,
    'Dark_str': 1,
    'Steel_str': 0.64,
    'Fairy_str': 1.25,
    'Normal_vuln': 1,
    'Fire_vuln': 1.25,
    'Water_vuln': 0.8,
    'Grass_vuln': 0.64,
    'Electric_vuln': 0.8,
    'Ice_vuln': 1.25,
    'Fighting_vuln': 0.8,
    'Poison_vuln': 1,
    'Ground_vuln': 1,
    'Flying_vuln': 1.25,
    'Psychic_vuln': 1.25,
    'Bug_vuln': 1,
    'Rock_vuln': 1,
    'Ghost_vuln': 1,
    'Dragon_vuln': 1,
    'Dark_vuln': 1,
    'Steel_vuln': 1,
    'Fairy_vuln': 0.8
}

CHARMANDER = {
    'Name': 'Charmander',
    'Pokemon': 'Charmander',
    'Level': 51,
    'IV attack': 13,
    'IV defence': 14,
    'IV HP': 15,
    'Number': 4,
    'Base attack': 116,
    'Base defence': 93,
    'Base HP': 118,
    'Type 1': 'Fire',
    'Type 2': '',
    'Max attack': 129,
    'Real attack': 109,
    'Max defence': 107,
    'Real defence': 90,
    'Max HP': 133,
    'Real HP': 112,
    'CP': 1099,
    'Multiplier': 0.84529999,
    'Fast attack': 'Ember',
    'Charged attack 1': 'Flamethrower',
    'Charged attack 2': 'Flame Charge',
    'Fast attack type': 'Fire',
    'Fast attack duration': 2,
    'Fast attack damage': 7,
    'Fast attack energy generated': 6,
    'Charged attack 1 type': 'Fire',
    'Charged attack 1 damage': 90,
    'Charged attack 1 energy cost': -55,
    'Charged attack 2 type': 'Fire',
    'Charged attack 2 damage': 65,
    'Charged attack 2 energy cost': -50,
    'Fast attack STAB': 1.2,
    'Charged attack 1 STAB': 1.2,
    'Charged attack 2 STAB': 1.2,
    'Attack cycle 1 length': 20,
    'Attack cycle 1 damage': 192,
    'DPT 1': 9.6,
    'Attack cycle 2 length': 18,
    'Attack cycle 2 damage': 153.6,
    'DPT 2': 8.53333333333334,
    'Normal_str': 1,
    'Fire_str': 0.64,
    'Water_str': 0.64,
    'Grass_str': 1.5625,
    'Electric_str': 1,
    'Ice_str': 1.5625,
    'Fighting_str': 1,
    'Poison_str': 1,
    'Ground_str': 1,
    'Flying_str': 1,
    'Psychic_str': 1,
    'Bug_str': 1.5625,
    'Rock_str': 0.64,
    'Ghost_str': 1,
    'Dragon_str': 0.64,
    'Dark_str': 1,
    'Steel_str': 1.5625,
    'Fairy_str': 1,
    'Normal_vuln': 1,
    'Fire_vuln': 0.8,
    'Water_vuln': 1.25,
    'Grass_vuln': 0.8,
    'Electric_vuln': 1,
    'Ice_vuln': 0.8,
    'Fighting_vuln': 1,
    'Poison_vuln': 1,
    'Ground_vuln': 1.25,
    'Flying_vuln': 1,
    'Psychic_vuln': 1,
    'Bug_vuln': 0.8,
    'Rock_vuln': 1.25,
    'Ghost_vuln': 1,
    'Dragon_vuln': 1,
    'Dark_vuln': 1,
    'Steel_vuln': 0.8,
    'Fairy_vuln': 0.8
}

PIDGEOT = {
    'Name': 'Pidgeot',
    'Pokemon': 'Pidgeot',
    'Level': 26,
    'IV attack': 12,
    'IV defence': 15,
    'IV HP': 15,
    'Number': 18,
    'Base attack': 166,
    'Base defence': 154,
    'Base HP': 195,
    'Type 1': 'Normal',
    'Type 2': 'Flying',
    'Max attack': 178,
    'Real attack': 121,
    'Max defence': 169,
    'Real defence': 115,
    'Max HP': 210,
    'Real HP': 143,
    'CP': 1555,
    'Multiplier': 0.6811649,
    'Fast attack': 'Steel Wing',
    'Charged attack 1': 'Brave Bird',
    'Charged attack 2': 'Hurricane',
    'Fast attack type': 'Steel',
    'Fast attack duration': 2,
    'Fast attack damage': 7,
    'Fast attack energy generated': 6,
    'Charged attack 1 type': 'Flying',
    'Charged attack 1 damage': 130,
    'Charged attack 1 energy cost': -55,
    'Charged attack 2 type': 'Flying',
    'Charged attack 2 damage': 110,
    'Charged attack 2 energy cost': -65,
    'Fast attack STAB': 1,
    'Charged attack 1 STAB': 1.2,
    'Charged attack 2 STAB': 1.2,
    'Attack cycle 1 length': 20,
    'Attack cycle 1 damage': 226,
    'DPT 1': 11.3,
    'Attack cycle 2 length': 22,
    'Attack cycle 2 damage': 209,
    'DPT 2': 9.5,
    'Normal_str': 1,
    'Fire_str': 1,
    'Water_str': 1,
    'Grass_str': 1.5625,
    'Electric_str': 0.64,
    'Ice_str': 1,
    'Fighting_str': 1.5625,
    'Poison_str': 1,
    'Ground_str': 1,
    'Flying_str': 1,
    'Psychic_str': 1,
    'Bug_str': 1.5625,
    'Rock_str': 0.64,
    'Ghost_str': 1,
    'Dragon_str': 1,
    'Dark_str': 1,
    'Steel_str': 0.64,
    'Fairy_str': 1,
    'Normal_vuln': 1,
    'Fire_vuln': 1,
    'Water_vuln': 1,
    'Grass_vuln': 0.8,
    'Electric_vuln': 1.25,
    'Ice_vuln': 1.25,
    'Fighting_vuln': 1,
    'Poison_vuln': 1,
    'Ground_vuln': 0.8,
    'Flying_vuln': 1,
    'Psychic_vuln': 1,
    'Bug_vuln': 0.8,
    'Rock_vuln': 1.25,
    'Ghost_vuln': 0.8,
    'Dragon_vuln': 1,
    'Dark_vuln': 1,
    'Steel_vuln': 1,
    'Fairy_vuln': 1
}

def test_evaluation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.evaluate_team([IVYSAUR, CHARMANDER, PIDGEOT]) == 1628.2857142857142

def test_explanation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    explanation = evaluation.explain_team([IVYSAUR, CHARMANDER, PIDGEOT])
    expected_explanation = {
        'attack': {
            'value': 354.0,
            'weight': 1
        },
        'attack-cycle-damage': {
            'value': 31.6142857142857,
            'weight': 10
        },
        'attack-cycle-length-inverted': {
            'value': 0.17142857142857143,
            'weight': 1500
        },
        'defence': {
            'value': 320.0,
            'weight': 1
        },
        'hp': {
            'value': 381.0,
            'weight': 1
        },
        'score': 1628.2857142857142,
        'type-vulnerability': {
            'value': 0.0,
            'weight': 100
        }
    }
    assert explanation == expected_explanation

def test_constraint_matching(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.matches_constraints(CHARMANDER)
    assert not evaluation.matches_constraints(PIDGEOT)

def test_attack_evaluation(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    assert evaluation.evaluate_attacks(IVYSAUR) == 17.85714285714284

def test_compare_evaluation_results(framework_setup):
    evaluation = retrieve_evaluations(read_store(DataType.EVALUATION))[0]
    result1 = EvaluationResult(team=[IVYSAUR, CHARMANDER, PIDGEOT], e=evaluation)
    evaluation.constraints[EvaluationColumn.MAX_CP_CONSTRAINT] = 1600
    result2 = EvaluationResult(team=[CHARMANDER, IVYSAUR, PIDGEOT], e=evaluation)

    assert result1 < result2
    assert result1 <= result2
    assert result2 <= result2
    assert result2 > result1
    assert result2 >= result1
    assert result2 >= result2
    assert result1 == result1
    assert result1 != {}
    assert result1 != result2
    assert repr(result1) == 'test-evaluation([\'Ivysaur\', \'Charmander\', \'Pidgeot\']) = 0'