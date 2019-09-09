""" Container Node Services """

from app.api.services.base_service import BaseService
from app.core.logging import LoggingFacility
from app.api.models import (DockerInfoDTO, SupervisordInfoDTO,
                           ToskoseNodeInfoDTO, LifecycleOperationInfoDTO,
                           HostedComponentInfoDTO)
from app.manager import ToskoseManager
from app.api.utils.utils import compute_uptime
from app.core.exceptions import (ClientConnectionError, FatalError,
                                 ClientFatalError, ClientOperationFailedError,
                                 OperationNotValid, ResourceNotFoundError)
from app.client.exceptions import (SupervisordClientFatalError,
                                   SupervisordClientProtocolError,
                                   SupervisordClientFaultError)
from app.config import AppConfig

from typing import List, Dict
from enum import Enum, auto


logger = LoggingFacility.get_instance().get_logger()


class LifecycleOperationActionType(Enum):
    START = auto()
    STOP = auto()
    INFO = auto()

class LogsActionType(Enum):
    READ = auto()
    TAIL = auto()
    CLEAR = auto()

class LogsType(Enum):
    NODE = auto()
    OPERATION = auto()

class NodeService(BaseService):

    SUPPORTED_LOGS_STD = ['stdout', 'stderr']

    def __init__(self):
        super().__init__()

    def initializer(validate_node=True, client=True):
        def decorator(func):
            def wrapper(self, *args, **kwargs):

                node_id = kwargs.get('node_id')

                """ validate the node identifier """
                if validate_node:
                    try:
                        ToskoseManager.get_instance().node_by_id(node_id)
                    except ValueError:
                        raise ResourceNotFoundError(
                            'node {0} not found'.format(node_id))

                """ get the client instance """
                if client:
                    self._client = \
                        ToskoseManager.get_instance().get_client(node_id)

                    if self._client is None:
                        raise OperationNotValid('Cannot operate on a standalone container.')

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

                return res
            return wrapper
        return decorator

    @staticmethod
    def __build_node_info_dto(*, node, client=None):
        """ builds the NodeInfoDTO

        If the node is not reacheable (client=None) the data fetched from the
        node API are omitted (using default value in the associated dataclass).
        ofc "the node" is the container node in the tosca model.
        """

        docker_data = {
            'image': node.toskosed_image.name,
            'tag': node.toskosed_image.tag,
        }

        supervisord_data = {}
        if client: 
            supervisord_data = {
                'hostname': node.hostname,
                'port': node.port,
                'username': node.user,
                'password': node.password,
                'log_level': node.log_level,
                'api_protocol': AppConfig._CLIENT_PROTOCOL,
                'hosted_components': [component.name for component in node.hosted],
            } 
            if client.reachable():
                supervisord_data.update({ 
                    'reachable': True,
                    'ip': client.ipv4,
                    'api_version': client.get_api_version(),
                    'supervisor_version': client.get_supervisor_version(),
                    'supervisor_id': client.get_identification(),
                    'supervisor_state':  \
                        (lambda x : {
                            'name': x['statename'],
                            'code': x['statecode']
                        })(client.get_state()),
                    'supervisor_pid': client.get_pid(),
                })          
                
        return ToskoseNodeInfoDTO(
            node_id=node.name,
            docker=DockerInfoDTO(**docker_data),
            supervisord=SupervisordInfoDTO(**supervisord_data),
            standalone=True if client is None else False
        )

    @staticmethod
    def __build_lifecycle_operation_info_dto(node_id, component_id, operation, res):
        return LifecycleOperationInfoDTO(
            node_id=node_id,
            component_id=component_id,
            operation=operation,
            description=res['description'],
            time_start=str(res['start']),
            time_end=str(res['stop']),
            uptime=compute_uptime(res['start'], res['stop']),
            state_code=str(res['state']),
            state_name=res['statename'],
            logfile_path=res['logfile'],
            stdout_logfile_path=res['stdout_logfile'],
            stderr_logfile_path=res['stderr_logfile'],
            spawn_error=res['spawnerr'],
            exit_status=str(res['exitstatus']),
            pid=str(res['pid'])
        )

    def get_all_nodes_info(self) -> List:
        """ Retrieve info about all the available nodes. """

        return [self.node_info(node.name) for node in ToskoseManager.get_instance().nodes]

    def node_info(self, node_id):
        """ Retrieve info about a node mixing info from the the application
        configuration and info fetched from the Node API through the client.
        """

        node = ToskoseManager.get_instance().node_by_id(node_id)
        client = ToskoseManager.get_instance().get_client(node.name)

        return NodeService.__build_node_info_dto(
            node=node,
            client=client)

    def hosted_component_info(self, node_id, component_id):
        """ Retrieve info about a component hosted on a node.
        e.g. lifecycle operations available
        """

        node = ToskoseManager.get_instance().node_by_id(node_id)
        for component in node.hosted:
            result = list()
            if component.name == component_id:
                for interface_k, interface_v in component.interfaces.items():
                    if interface_k.upper() == 'STANDARD':
                        logger.debug('Extracting Standard interfaces from [{}]'.format(
                            component_id))
                        result += [std_int for std_int in interface_v.keys()]
                    else:
                        logger.debug('Extracting custom interfaces [{0}] from [{1}]'.format(
                            interface_k, component_id))
                        result += [custom_int for custom_int in interface_v.keys()]
                return HostedComponentInfoDTO(
                    component_id=component_id,
                    lifecycle_operations=result)
                        
        raise ResourceNotFoundError('{0} not hosted on node {1}'.format(
            component_id, node_id))

    @initializer()
    def execute(self, *, node_id, component_id, operation, action, wait=True):
        """ Manage a lifecycle operation of a software component hosted on a container node.

        Args:
            node_id (str): The identifier of the container node.
            component_id (str): The identifier of the hosted component.
            operation (str): The operation to be executed.
            action (Enum): The type of action to do with the lifecycle operation.
            wait (bool): wait for lifecycle operation to be fully started.
        
        An example of Supervisord program: [program:component_id-operation]
        e.g. [program:api-create]

        """

        BLOCK_EXECUTION_STATES = ['STARTING', 'RUNNING', 'BACKOFF']

        assert isinstance(action, LifecycleOperationActionType)

        name = '{0}-{1}'.format(component_id, operation)
        logger.debug('[{0}] lifecycle operation [{1}] on component [{2}] over [{3}] node'.format(
            action.name, operation, component_id, node_id))

        if action is LifecycleOperationActionType.START:

            # check if the same lifecycle operation is still running
            lifecycle_operation = self.execute(
                node_id=node_id, component_id=component_id, operation=operation, 
                action=LifecycleOperationActionType.INFO)
            if lifecycle_operation.state_name in BLOCK_EXECUTION_STATES:
                raise OperationNotValid(
                    'Cannot start the operation because it\'s already in [{}] state'.format(
                        lifecycle_operation.state_name))
            return self._client.start_process(name, wait)
        elif action is LifecycleOperationActionType.STOP:
            return self._client.stop_process(name, wait)
        elif action is LifecycleOperationActionType.INFO:
            return NodeService.__build_lifecycle_operation_info_dto(
                node_id, component_id, operation,
                self._client.get_process_info(name))
        else:
            logger.warn('An invalid action [{0}] is occurred.'.format(
                    action.name))
            raise FatalError('A fatal error is occurred.')

    def stop_all_operations(self, *, node_id, wait=True):
        """ Stop all the lifecycle operations running on the node. 
        
        Args:
            node_id (str): The node identifier.
            wait (bool): wait for all lifecycle operations to be terminated.
        """

        return self._client.stop_all_processes(wait)

    @initializer()
    def node_logs(self, *, node_id, action, offset=0, length=0):
        """ Manage node logs. """

        assert isinstance(action, LogsActionType)

        if action is LogsActionType.READ:
            return self._client.read_log(offset, length)
        if action is LogsActionType.CLEAR:
            return self._client.clear_log()

    @initializer()
    def operation_logs(self, *, node_id, action, component_id, operation, 
                       offset=0, length=0, std_type='stdout'):
        """ Manage lifecycle operation logs. """

        assert isinstance(action, LogsActionType)
        name = '{0}-{1}'.format(component_id, operation)

        if std_type not in NodeService.SUPPORTED_LOGS_STD:
            logger.warn('{} logs channel not supported'.format(std_type))
            raise OperationNotValid('The std {} is not supported yet.'.format(std_type))

        if action is LogsActionType.READ:
            if std_type == 'stdout':
                return self._client.read_process_stdout_log(name, offset, length)
            if std_type == 'stderr':
                return self._client.read_process_stderr_log(name, offset, length) 
        if action is LogsActionType.TAIL:
            return 'Not implemented yet. Apologize <3'
        if action is LogsActionType.CLEAR:
            return self._client.clear_process_log(name)

    """ not implemented """

    def reload_config(self):
        """ Reload the Supervisord config """
        #self._client.reload_config()
        pass

    def send_remote_comm_event(self, *, node_id, type, data):
        """ not implemented yet """
        pass

    def add_process_group(self, *, node_id, name):
        """ not implemented yet """
        pass

    def remove_process_group(self, *, node_id, name):
        """ not implemented yet """
        pass

    def list_methods(self, *, node_id):
        """ not implemented yet """
        pass

    def method_help(self, *, node_id, name):
        """ not implemented yet """
        pass

    def method_signature(self, *, node_id, name):
        """ not implemented yet """
        pass

    def multicall(self, *, node_id, calls):
        """ not implemented yet """
        pass
