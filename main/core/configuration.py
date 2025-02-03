'''
Application configuration logic.
'''
import logging
import sys
from typing import Any
import yaml

from main.core.singleton import Singleton

logger = logging.getLogger(__name__)

class ConfigurationException(Exception):
    '''
    Exception class used to indicate a user error in configuration.
    '''

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.message = args[0]


class ConfigurationService(Singleton):
    '''
    A class that acts as a configuration parser and repository. Supports YAML
    configuration files and single key-value configuration properties. Keeps
    configurations for the four key parts of this application (data source, filters,
    transformers, data sink) separate for convenience.
    '''

    def __init__(self) -> None:
        if self.initialised:
            return
        self.configuration: dict[str, Any] = {}
        self.initialised = True

    def parse_configuration_file(self, filename: str) -> None:
        '''
        Opens and parses the file with the provided name as a YAML file.
        '''
        logger.info('Parsing configuration file %s', filename)
        with open(filename, 'r', encoding='utf8') as configuration_file:
            self.configuration = yaml.safe_load(configuration_file)

    def set_configuration_property(self, key: str, value: Any) -> None:
        '''
        Accepts an individual key-value pair as a configuration override.
        Supports the key being a full-stop-separated path in the configuration tree,
        e.g. if called with key1.key2=value, it will create a configuration like:
        {
            'key1': {
                'key2': 'value'
            }
        }

        NB: The configuration tree traversal does not currently support lists, e.g.
        it does _not_ provide a way of creating a configuration like
        {
            'key': [
                'value'
            ]
        }
        '''
        logger.info('Additional configuration property from command line: %s=%s', key, value)
        path: list[str] = key.split('.')
        current_configuration: dict[str, Any] = self.configuration
        # tree traversal, creating any missing nodes along the way
        for path_segment in path[:-1]:
            if path_segment not in current_configuration:
                current_configuration[path_segment] = {}
            current_configuration = current_configuration[path_segment]
        current_configuration[path[-1]] = value

    def get_configuration_property(
            self,
            key: str,
            default: Any = None) -> Any:
        '''
        Convenience function for getting a member of a configuration dictionary and either
        returning the default if it the member is missing, or raising ConfigurationException
        if the default is not declared.
        '''
        current_configuration: dict[str, Any] = self.configuration
        path: list[str] = key.split('.')
        for path_segment in path[:-1]:
            if path_segment not in current_configuration:
                if default is not None:
                    return default
                raise ConfigurationException(
                    f'Missing required property {key} from configuration')
            current_configuration = current_configuration[path_segment]
        return current_configuration[path[-1]] if path[-1] in current_configuration else default


def configure():
    '''
    Framework entry point. Treats every command line argument as a configuration source:
    if the argument contains a '=' character, treats it as a key-value configuration
    override; otherwise, treats it as a YAML file. After parsing the command line arguments,
    calls the main flow of the application.
    '''
    configuration_filenames: list[str] = []
    additional_configuration: dict[str, str] = {}
    for arg in sys.argv[1:]:
        if '=' in arg:
            additional_configuration[arg.split('=')[0]] = arg.split('=')[1]
        else:
            configuration_filenames.append(arg)
    for configuration_filename in configuration_filenames:
        ConfigurationService().parse_configuration_file(configuration_filename)
    for key, value in additional_configuration.items():
        ConfigurationService().set_configuration_property(key, value)
