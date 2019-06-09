from enum import Enum, auto
from app.client.impl.xmlrpc_client import ToskoseXMLRPCclient
from app.client.impl.docker_client import DockerClient


class ProtocolType(Enum):
    XMLRPC = auto()
    DOCKER = auto()

class ToskoseClientFactory:

    @staticmethod
    def create(*, protocol_type, **kwargs):
        protocol_type = protocol_type.upper()
        if protocol_type == ProtocolType.XMLRPC.name:
            return ToskoseXMLRPCclient(**kwargs)
        elif protocol_type == ProtocolType.DOCKER.name:
            return DockerClient(**kwargs, standalone=True)
        else:
            raise ValueError("Invalid client protocol: {}".format(protocol_type))
