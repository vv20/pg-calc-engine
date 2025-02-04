'''
Implementation of the singleton pattern.
'''
class Singleton:
    '''
    A class that always returns the same instance when it is instantiated, i.e.

        Singleton() is Singleton()
        
    NB: In the current implementation, the __init__ method is still called every
        time the class is instantiated. For convenience, the class also declares
        the _initialised field that can be used to track whether the __init__
        method has been called already and skip initialisation; however, the
        responsibility for using the field lies with the subclasses of Singleton.
    '''

    _instance: object = None
    initialised: bool = False

    def __new__(cls) -> object:
        if cls._instance is None:
            cls._instance: Singleton = object.__new__(cls)
        return cls._instance
