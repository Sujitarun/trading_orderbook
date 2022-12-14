import pytest

from src import start as _start


@pytest.fixture
def start():
    return _start
