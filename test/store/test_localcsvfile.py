from pandas import DataFrame
import pytest
from unittest.mock import call, patch, MagicMock

from main.core.configuration import ConfigurationException
from main.store import clear_cache, read_store, write_store, DataType

from test.util import framework_setup

MOCK_VALUES = DataFrame({
    'Header1' : ['Row1Col1', 'Row2Col1'],
    'Header2' : ['Row1Col2', 'Row2Col2'],
    'Header3' : ['Row1Col3', 'Row2Col3']
})

@pytest.fixture
def localcsv_setup(mocker):
    mock_read_csv = mocker.patch('main.store.localcsvfile.read_csv')
    mock_read_csv.return_value = MOCK_VALUES

    mock_path_exists = mocker.patch('main.store.localcsvfile.os.path.exists')
    mock_path_exists.return_value = True

    mock_isdir = mocker.patch('main.store.localcsvfile.os.path.isdir')
    mock_isdir.return_value = True

    mock_mkdir = mocker.patch('main.store.localcsvfile.os.mkdir')
    
    mock_open = mocker.patch('main.store.localcsvfile.open')
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    yield {
        'mock_read_csv': mock_read_csv,
        'mock_path_exists': mock_path_exists,
        'mock_isdir': mock_isdir,
        'mock_mkdir': mock_mkdir,
        'mock_open': mock_open,
        'mock_file': mock_file
    }

def test_read_store(framework_setup, localcsv_setup):
    mock_read_csv = localcsv_setup['mock_read_csv']
    clear_cache(DataType.ENRICHED_LIBRARY)

    df = read_store(DataType.ENRICHED_LIBRARY)

    mock_read_csv.assert_called_once_with('test/temp/enriched-library.csv')
    assert df.equals(MOCK_VALUES)

def test_read_store_paginated(framework_setup, localcsv_setup):
    mock_read_csv = localcsv_setup['mock_read_csv']
    clear_cache(DataType.ENRICHED_LIBRARY)

    df = read_store(DataType.ENRICHED_LIBRARY, page_title='page-title')

    mock_read_csv.assert_called_once_with('test/temp/enriched-library.page-title.csv')
    assert df.equals(MOCK_VALUES)

def test_read_store_cached(framework_setup, localcsv_setup):
    mock_read_csv = localcsv_setup['mock_read_csv']
    clear_cache(DataType.ENRICHED_LIBRARY)

    read_store(DataType.ENRICHED_LIBRARY)
    df = read_store(DataType.ENRICHED_LIBRARY)

    mock_read_csv.assert_called_once_with('test/temp/enriched-library.csv')
    assert df.equals(MOCK_VALUES)

def test_read_store_directory_does_not_exist(framework_setup, localcsv_setup):
    mock_path_exists = localcsv_setup['mock_path_exists']
    mock_mkdir = localcsv_setup['mock_mkdir']
    mock_path_exists.return_value = False
    clear_cache(DataType.ENRICHED_LIBRARY)

    read_store(DataType.ENRICHED_LIBRARY)

    mock_mkdir.assert_any_call('test/temp')

def test_read_store_directory_is_not_directory(framework_setup, localcsv_setup):
    mock_isdir = localcsv_setup['mock_isdir']
    mock_isdir.return_value = False
    clear_cache(DataType.ENRICHED_LIBRARY)
    with pytest.raises(ConfigurationException, match='test/temp is not a directory'):
        read_store(DataType.ENRICHED_LIBRARY)

def test_read_store_file_not_found(framework_setup, localcsv_setup):
    mock_path_exists = localcsv_setup['mock_path_exists']
    mock_path_exists.return_value = False
    clear_cache(DataType.ENRICHED_LIBRARY)

    df = read_store(DataType.ENRICHED_LIBRARY)
    
    assert df.empty

def test_write_store(framework_setup, localcsv_setup):
    mock_open = localcsv_setup['mock_open']
    mock_file = localcsv_setup['mock_file']
    data = MagicMock(spec=DataFrame)

    write_store(DataType.ENRICHED_LIBRARY, data)

    mock_open.assert_called_once_with('test/temp/enriched-library.csv', 'w', encoding='utf8')
    data.to_csv.assert_called_once_with(mock_file, index=False)

def test_write_store_paginated(framework_setup, localcsv_setup):
    mock_open = localcsv_setup['mock_open']
    mock_file = localcsv_setup['mock_file']
    data = MagicMock(spec=DataFrame)

    write_store(data_type=DataType.ENRICHED_LIBRARY, data=data, page_title='page-title')

    mock_open.assert_called_once_with('test/temp/enriched-library.page-title.csv', 'w', encoding='utf8')
    data.to_csv.assert_called_once_with(mock_file, index=False)

def test_read_store_after_write(framework_setup, localcsv_setup):
    data = MagicMock(spec=DataFrame)

    write_store(data_type=DataType.ENRICHED_LIBRARY, data=data)
    df = read_store(DataType.ENRICHED_LIBRARY)

    assert df == data