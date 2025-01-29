import logging

from main.core.configuration import ConfigurationException
from main.core.singleton import Singleton

logger = logging.getLogger(__name__)

class Factory(Singleton):
    '''
    A class that acts as a repository for mapping configuration types to implementations
    and constructs instances of implementation classes based on configuration.
    '''

    def __init__(self) -> None:
        super().__init__()
        if self._initialised:
            return
        self.types: dict[str, function] = {}
        self._initialised: bool = True

    def construct(self, type_: str, **kwargs) -> object:
        '''
        Factory method for constructing an implementation instance based on a
        configuration. The configuration must contain the key 'type', and the value
        associated with that key must be a string that has been registered as a type
        previously. If either of those conditions is not fulfilled, the method will
        raise a ConfigurationException.
        '''
        if type_ not in self.types:
            raise ConfigurationException('Could not find a type adapter for type ' + type_ + ' and factory ' + str(type(self)))
        logger.debug('Constructing a %s', self.types[type_])
        return self.types[type_](**kwargs)

    def register_type(self, type_: str, cls: type):
        '''
        Register a class as a type with the factory.
        '''
        logger.debug('Registering %s as type %s for factory %s', cls, type_, self.__class__)
        self.types[type_] = cls


def factory_register(type_: str, factory: Factory):
    '''
    Decorator for registering classes as types with the provided factory.
    '''
    def specific_factory_register(cls: type):
        logger.debug('Registering %s as type %s for factory %s', cls, type_, factory.__class__)
        factory.types[type_] = cls
    return specific_factory_register