import pytest
import mock
import os

from tests.helpers import full_path

# Note: set envs in tests
# e.g. for setup the LoggingFactory we need an env TOSKOSE_LOGS_PATH
# https://stackoverflow.com/questions/41430465/environment-variables-with-pytest-and-tox
# Options:
# - mock and patch os.environ
# - set/unset envs with setUp() and tearDown()
# - use the pytest-env plugin (https://pypi.org/project/pytest-env/)

# Use monkeypatch pytest's fixture!
# https://docs.pytest.org/en/latest/monkeypatch.html


def test_initialization(monkeypatch):
    monkeypatch.setenv("TOSKOSE_CONFIG_PATH", full_path('thinking/config'))
    monkeypatch.setenv("TOSKOSE_MANIFEST_PATH", full_path('thinking/manifest'))
    
    # avoid initialization of AppConfig class with default envs before the monkeypatch
    from app.manager import ToskoseManager
    
    ToskoseManager.get_instance().initialization()
