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
    n_partitions = distribute_handler()
    assert n_partitions == 10
    for i in range(n_partitions):
        evaluate_handler(event={'partition_number': i}, context={})
    reduce_handler()
    result = read_store(DataType.RESULT, page_title='integration-test-evaluation')
    assert len(result) == 10
    top_row = result.sort_values(by=['result'], ascending=False).iloc[0].to_dict()
    assert explain_handler(event={'pokemon_names': [top_row['1'], top_row['2'], top_row['3']], 'evaluation_name': 'integration-test-evaluation'}, context={}) == {
        'attack': {
            'value': 322.0,
            'weight': 1
        },
        'attack-cycle-damage': {
            'value': 24.11813186813187,
            'weight': 10
        },
        'attack-cycle-length-inverted': {
            'value': 0.1304945054945055,
            'weight': 1500
        },
        'defence': {
            'value': 312.0,
            'weight': 1
        },
        'hp': {
            'value': 346.0,
            'weight': 1
        },
        'score': 1416.9230769230771,
        'type-vulnerability': {
            'value': 0.0,
            'weight': 100
        }
    }