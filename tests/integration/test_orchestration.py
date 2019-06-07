import pytest
import requests

from app.core.toskose_manager import ToskoseManager


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


# note: docker_ip, docker_services fixtures are part of 
# the pytest-docker plugin

@pytest.fixture(scope='session')
def containers(docker_ip, docker_services):
    """ wait until all container are up and running """

    


def test_orchestration(containers):
    pass