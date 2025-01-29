import pytest
from typing import Any

from main.core.configuration import ConfigurationException
from main.core.factory import factory_register, Factory

class DummyFactory(Factory):
    pass

@factory_register('test1', DummyFactory())
class Instance1(object):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

class Instance2(object):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

def test_factory_constructs_object_from_type_registered_with_decorator():
    kwargs: dict[str, Any] = {
        'dependency': 3
    }
    instance: Instance1 = DummyFactory().construct('test1', **kwargs)
    assert instance.kwargs == kwargs

def test_factory_constructs_object_from_type_registered_with_method_call():
    DummyFactory().register_type('test2', Instance2)
    kwargs: dict[str, Any] = {
        'dependency': 3
    }
    instance: Instance2 = DummyFactory().construct('test2', **kwargs)
    assert instance.kwargs == kwargs

def test_factory_raises_exception_for_undefined_type():
    with pytest.raises(ConfigurationException, match='Could not find a type adapter for type not-a-type and factory <class \'test.core.test_factory.DummyFactory\'>'):
        DummyFactory().construct('not-a-type')