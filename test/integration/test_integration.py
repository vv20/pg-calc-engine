import pytest

from main.core.configuration import configure
from main.handler.distribute import handler as distribute_handler
from main.handler.enrich import handler as enrich_handler
from main.handler.evaluate import handler as evaluate_handler
from main.handler.explain import handler as explain_handler
from main.handler.reduce import handler as reduce_handler
from main.store import read_store, DataType

@pytest.fixture
def setup(mocker):
    mock_sys = mocker.patch('main.core.configuration.sys')
    mock_sys.argv = [
        'main.py',
        'test/integration/configuration/integration-test-configuration.yaml'
    ]
    configure()

def test_integration(setup):
    enrich_handler()
    partitions = distribute_handler()
    assert len(partitions) == 84
    for partition in partitions:
        evaluate_handler(event={'permutation': partition}, context={})
    reduce_handler()
    result = read_store(DataType.RESULT, page_title='integration-test-evaluation')
    assert len(result) == 10
    top_row = result.sort_values(by=['result'], ascending=False).iloc[0].to_dict()
    assert explain_handler(event={'pokemon_names': [top_row['1'], top_row['2'], top_row['3']], 'evaluation_name': 'integration-test-evaluation'}, context={}) == {
        'attack': {
            'value': 391.0,
            'weight': 1
        },
        'attack-cycle-damage': {
            'value': 38.31428571428572,
            'weight': 10
        },
        'attack-cycle-length-inverted': {
            'value': 0.27142857142857146,
            'weight': 1500
        },
        'defence': {
            'value': 328.0,
            'weight': 1
        },
        'hp': {
            'value': 343.0,
            'weight': 1
        },
        'score': 1852.2857142857142,
        'type-vulnerability': {
            'value': 0.0,
            'weight': 100
        }
    }