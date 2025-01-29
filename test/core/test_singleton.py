from main.core.singleton import Singleton

class DummySingleton(Singleton):
    
    def __init__(self) -> None:
        super().__init__()
        if self._initialised:
            return
        self.counter: int = 1
        self._initialised = True

def test_singleton_is_always_the_same():
    instance1: DummySingleton = DummySingleton()
    instance2: DummySingleton = DummySingleton()
    assert instance1 is instance2

def test_singleton_should_keep_state_between_ctor_calls():
    instance: DummySingleton = DummySingleton()
    instance.counter = 2
    assert DummySingleton().counter == 2