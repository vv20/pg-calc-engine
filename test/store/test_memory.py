from pandas import DataFrame

from main.store import clear_cache, read_store, write_store, DataType

from test.util import framework_setup

MOCK_VALUES = DataFrame({
    'Header1' : ['Row1Col1', 'Row2Col1'],
    'Header2' : ['Row1Col2', 'Row2Col2'],
    'Header3' : ['Row1Col3', 'Row2Col3']
})

def test_read_write(framework_setup):
    write_store(DataType.CACHE, MOCK_VALUES)
    assert read_store(DataType.CACHE).equals(MOCK_VALUES)

def test_read_write_paginated(framework_setup):
    write_store(DataType.CACHE, MOCK_VALUES, page_title='page-title')
    assert read_store(DataType.CACHE, page_title='page-title').equals(MOCK_VALUES)

def test_read_cache_miss(framework_setup):
    clear_cache(DataType.CACHE)
    assert read_store(DataType.CACHE).empty