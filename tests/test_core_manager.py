import pytest
import mock
import os
import tempfile

from distutils.dir_util import copy_tree

from tests.helpers import full_path
from app.core.toskose_manager import ToskoseManager
from app.core.loader import Loader

# Note: set envs in tests
# e.g. for setup the LoggingFactory we need an env TOSKOSE_LOGS_PATH
# https://stackoverflow.com/questions/41430465/environment-variables-with-pytest-and-tox
# Options:
# - mock and patch os.environ
# - set/unset envs with setUp() and tearDown()
# - use the pytest-env plugin (https://pypi.org/project/pytest-env/)

root_dir = full_path('thinking')

def test_loading_with_name():
    with tempfile.TemporaryDirectory() as tmp:
        # copy test files to a tmp folder
        copy_tree(root_dir, tmp)
        ToskoseManager().get_instance().load(
                config_dir=os.path.join(tmp, 'config'),
                manifest_dir=os.path.join(tmp, 'manifest'))

def test_get_client():
    with tempfile.TemporaryDirectory() as tmp:
        # copy test files to a tmp folder
        copy_tree(root_dir, tmp)
        ToskoseManager().get_instance().load(
                config_dir=os.path.join(tmp, 'config'),
                manifest_dir=os.path.join(tmp, 'manifest'))
        
        # test
        cfg = Loader().load(os.path.join(root_dir, 'config/toskose.yml'))
        for k,v in cfg['nodes'].items():
            client = ToskoseManager.get_instance().get_client(k)
            assert True