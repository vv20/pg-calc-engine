from pandas import DataFrame
import pytest

from main.store import read_store, write_store, DataType

from test.util import framework_setup

def test_evaluation_data_from_configuration(framework_setup):
    evaluation_data: DataFrame = read_store(DataType.EVALUATION)
    assert len(evaluation_data) == 1

def test_configuration_store_does_not_support_pages(framework_setup):
    with pytest.raises(Exception, match='Pagination not supported for configuration storage'):
        read_store(DataType.EVALUATION, 'page')

def test_configuration_store_only_supports_evaluation_data(framework_setup):
    with pytest.raises(Exception, match='Data type cpm-reference-data not supported for configuration storage'):
        read_store(DataType.CPM_REFERENCE_DATA)

def test_configuration_store_does_not_support_writing(framework_setup):
    with pytest.raises(Exception, match='Writing not supported for configuration storage'):
        write_store(DataType.EVALUATION, DataFrame())