import pytest

from main.core.configuration import ConfigurationException, ConfigurationService

from test.util import framework_setup

def test_configuration_service_parses_configuration_file(framework_setup):
    assert ConfigurationService().get_configuration_property('file-property') == 'file-value'

def test_configuration_service_parses_configuration_arg(framework_setup):
    assert ConfigurationService().get_configuration_property('cmd-property') == 'cmd-value'

def test_configuration_service_inserts_defaults(framework_setup):
    assert ConfigurationService().get_configuration_property('prefix.not-a-property', default='default') == 'default'

def test_configuration_service_raises_exception_on_missing_property(framework_setup):
    with pytest.raises(ConfigurationException, match='Missing required property prefix.not-a-property from configuration'):
        ConfigurationService().get_configuration_property('prefix.not-a-property')

def test_set_configuration_property_sets_property(framework_setup):
    ConfigurationService().set_configuration_property('prefix.new-property', 'new-value')
    assert ConfigurationService().get_configuration_property('prefix.new-property') == 'new-value'