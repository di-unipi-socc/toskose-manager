from app.core.logging import LoggingFacility
from app.manager import ToskoseManager

from app.client.exceptions import SupervisordClientConnectionError
from app.client.exceptions import SupervisordClientFatalError
from app.client.exceptions import SupervisordClientProtocolError
from app.client.exceptions import SupervisordClientFaultError

from app.core.exceptions import FatalError
from app.core.exceptions import ClientFatalError
from app.core.exceptions import ClientOperationFailedError
from app.core.exceptions import ClientConnectionError
from app.core.exceptions import OperationNotValid
from app.core.exceptions import ResourceNotFoundError


logger = LoggingFacility.get_instance().get_logger()


class BaseService():

    """ client decorators

    init_client() instantiates the client and check node\'s reachability.
    If the validate_connection argument is set to False, then it suppresses the
    SupervisordConnectionError, so it will not be catched by the api errorhandler,
    but a boolean istance attribute regarding the reachability (is_reacheable)
    is always stored.
    This strategy meets the requirements to give partial info about the nodes
    (e.g. get_node_info() in NodeService) without raise an exception to the api
    controller, even if the node is offline.
    If the validate_connection argument is set to True, then the client is
    triggered before the function calling, and a SupervisordConnectionError
    will be raised if the node is offline.

    """

    @classmethod
    def init_client(cls, validate_node=False, validate_connection=False):
        def decorator(func):
            def wrapper(self, *args, **kwargs):

                node_id = kwargs.get('node_id')

                """ validate the node identifier """
                if validate_node:
                    
                    if not ToskoseManager.get_instance().get_node_data(
                        node_id=node_id):
                        raise ResourceNotFoundError(
                            'node {0} not found'.format(node_id))

                """ get the client instance """
                self._client = \
                    ToskoseManager.get_instance().get_client(node_id)

                """ validate connection: check the reachability of the node """
                if validate_connection:
                    if not self._client.reachable():
                        logger.error('[{}] node cannot be reached. (connection error)'.format(node_id))
                        raise ClientConnectionError(
                            'node {0} is offline'.format(node_id))

                try:
                    res = func(self, *args, **kwargs)
                except (SupervisordClientFaultError, SupervisordClientProtocolError) as err:
                    logger.warn(err)
                    raise ClientOperationFailedError(str(err)) from err
                except SupervisordClientFatalError as err:
                    logger.warn(err)
                    raise ClientFatalError('A Fatal error from the client is occurred') from err
                except OperationNotValid as err:
                    logger.warn(err)
                    raise ClientFatalError('An invalid operation is occurred') from err
                except:
                    logger.warn(err)
                    raise FatalError('An unexpected error is occurred')

                return res

            return wrapper
        return decorator

    def __init__(self):
        pass
