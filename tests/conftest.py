# pytest configurations

import pytest
import os

docker_compose_path = 'tests/data/thinking/docker-compose.yml'

@pytest.fixture(scope='session')
def docker_compose_file(pytestconfig):
    """ configure the docker-compose.yml location """
    return os.path.join(
        str(pytestconfig.rootdir),
        docker_compose_path)