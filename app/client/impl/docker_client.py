from app.core.logging import LoggingFacility

from app.client.impl.base_client import BaseClient


logger = LoggingFacility.get_instance().get_logger()


class DockerClient(BaseClient):
    """ Client for handling operation between containers. """

    def __init__(self, **kwargs):
        super(DockerClient, self).__init__(**kwargs)

    def is_reacheable(self):
        #TODO
        pass
