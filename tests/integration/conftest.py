# pytest configurations

import pytest
import os
import requests

docker_compose_path = 'tests/data/thinking/docker-compose.yml'

def is_responsive(url):
    """ Check if an HTTP service is available. """
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False

# docker-compose custom location (override default fixture)
@pytest.fixture(scope='session')
def docker_compose_file(request, pytestconfig):
    return os.path.join(
        # str(pytestconfig.rootdir),
        os.getcwd(),
        request.param
    )