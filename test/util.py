import pytest

from main.core.configuration import configure

@pytest.fixture
def framework_setup(mocker):
    mock_sys = mocker.patch('main.core.configuration.sys')
    mock_sys.argv = [
        'main.py',
        'test/test-assets/test-configuration.yaml',
        'cmd-property=cmd-value'
    ]
    configure()