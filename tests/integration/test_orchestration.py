""" Integration test of Thinking application with docker-compose """

import pytest
import os


docker_compose_path = [
	'tests/data/thinking/docker-compose.yml',
	'tests/data/sockshop/docker-compose.yml'
]

# container_name : supervisord_port
data = [
	{
		'thinking-maven': 9001,
		'thinking-node': 9002,
		'thinking-mongodb': 27017 # mongodb default port (no supervisord)
	},
]

protocol = [
    ({'thinking-maven': ''})
]

# https://stackoverflow.com/questions/52047176/py-test-parameterized-fixtures
# https://docs.pytest.org/en/latest/example/parametrize.html
@pytest.mark.parametrize('docker_compose_file', docker_compose_path, indirect=True)
@pytest.mark.parametrize('data', data)
def test_orchestration(docker_compose_file, data):
    
    pass