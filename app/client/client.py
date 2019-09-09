from enum import Enum, auto
from app.client.impl.xmlrpc_client import ToskoseXMLRPCclient


class ProtocolType(Enum):
    XMLRPC = auto()

class ToskoseClientFactory:

    @staticmethod
    def create(*, protocol_type, **kwargs):
        protocol_type = protocol_type.upper()
        if protocol_type == ProtocolType.XMLRPC.name:
            return ToskoseXMLRPCclient(**kwargs)
        else:
            raise ValueError("Invalid client protocol: {}".format(protocol_type))
