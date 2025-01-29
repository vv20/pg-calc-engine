from pandas import DataFrame
from typing import Any

from main.core.configuration import configure
from main.model.evaluation import Evaluation
from main.model.library import LibraryColumn
from main.store import read_store, DataType

def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    configure()
    library: DataFrame = read_store(DataType.ENRICHED_LIBRARY)
    evaluation_data: DataFrame = read_store(DataType.EVALUATION)
    evaluations = []
    for evaluation_data_row in evaluation_data.to_dict('records'):
        evaluation: Evaluation = Evaluation(evaluation_data_row)
        evaluations.append(evaluation)
    team: list[dict[str, Any]] = [
        library[library[LibraryColumn.POKEMON_NAME.value] == event['pokemon_names'][0]].to_dict('records')[0],
        library[library[LibraryColumn.POKEMON_NAME.value] == event['pokemon_names'][1]].to_dict('records')[0],
        library[library[LibraryColumn.POKEMON_NAME.value] == event['pokemon_names'][2]].to_dict('records')[0],
    ]
    evaluation: Evaluation = [e for e in evaluations if e.evaluation_name == event['evaluation_name']][0]
    return evaluation.explain_team(team)

if __name__ == '__main__':
    print(handler({
        'pokemon_names': [
            'Magneton', 'Malamar', 'Dubwool'
        ],
        'evaluation_name': 'my-first-gl-evaluation'
    }, {}))