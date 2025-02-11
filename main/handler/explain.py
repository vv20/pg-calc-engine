'''
Logic to drill down into an evaluation result and the feature values
that constitute it.
'''
from typing import Any

from pandas import DataFrame

from main.core.configuration import configure
from main.model.evaluation import Evaluation, retrieve_evaluations
from main.model.library import LibraryColumn
from main.store import read_store, DataType

def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    '''
    Produce a breakdown of the score of a team according to an evaluation model.
    The breakdown contains the value of each feature, along with the weight
    of the feature, and the overall result.
    '''
    configure()
    lib: DataFrame = read_store(DataType.ENRICHED_LIBRARY, page_title=event['evaluation_name'])
    pokemon_names: list[str] = event['pokemon_names']
    team: list[dict[str, Any]] = [
        lib[lib[LibraryColumn.POKEMON_NAME.value] == pokemon_names[0]].to_dict('records')[0],
        lib[lib[LibraryColumn.POKEMON_NAME.value] == pokemon_names[1]].to_dict('records')[0],
        lib[lib[LibraryColumn.POKEMON_NAME.value] == pokemon_names[2]].to_dict('records')[0],
    ]
    evaluation: Evaluation = [e for e in retrieve_evaluations(
        read_store(DataType.EVALUATION)) if e.evaluation_name == event['evaluation_name']][0]
    return evaluation.explain_team(team)

if __name__ == '__main__':
    print(handler({
        'pokemon_names': [
            'Magneton', 'Malamar', 'Dubwool'
        ],
        'evaluation_name': 'my-first-gl-evaluation'
    }, {}))
