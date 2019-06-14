from flask_restplus import Namespace, fields
from dataclasses import dataclass, field
from typing import Dict, List

"""
Node Namespace
"""
ns_toskose_node = Namespace(
    'node',
    description='Operations for managing the nodes.'
)

"""
Node Schemas
"""
toskose_node = ns_toskose_node.model('ToskoseNode', {
    'node_id': fields.String(
        required=True,
        description='The node\'s identifier'
    ),
    'hosted_components': fields.List(
        fields.String,
        required=True,
        description='A list of software components hosted on the node'
    ),
    'reachable': fields.Boolean(
        required=True,
        description='A system message for reporting any errors occurred'
    ),
    'standalone': fields.Boolean(
        required=True,
        description='Identify if the node is a standalone container (without any management logic) or not'
    ),
    'docker': fields.Nested(ns_toskose_node.model('Docker', {
        'hostname': fields.String(
            required=True,
            description='The node\'s hostname'
        ),
        'ip': fields.String(
            required=True,
            description='The IPv4 of the node'
        ),
        'image': fields.String(
            required=True,
            description='The docker image of the node'
        ),
        'tag': fields.String(
            required=True,
            description='The tag of the docker image of the node'
        )
    }))
})

toskose_node_info = ns_toskose_node.inherit('ToskoseNodeInfo', toskose_node, {
    'supervisord': fields.Nested(ns_toskose_node.model('Supervisord', {
        'port': fields.String(
            required=True,
            description='The node\'s port'
        ),
        'username': fields.String(
            required=True,
            description='The node\'s username'
        ),
        'password': fields.String(
            required=True,
            description='The node\'s password'
        ),
        'log_level': fields.String(
            required=True,
            description='The node\'s log level'
        ),
        'api_protocol': fields.String(
            required=True,
            description='The protocol used for communicating with the node API'
        ),
        'api_version': fields.String(
            required=True,
            description='The node API version'
        ),
        'supervisor_version': fields.String(
            required=True,
            description='The version of the hosted Supervisor instance'
        ),
        'supervisor_id': fields.String(
            required=True,
            description='The identifier of the hosted Supervisor instance'
        ),
        'supervisor_state': fields.Nested(ns_toskose_node.model('Data', {
            'name': fields.String(
                required=True,
                description='The name of the state'),
            'code': fields.String(
                required=True,
                description='The code of the state')
            }),
            required=True,
            description='The state of the hosted Supervisor instance'
        ),
        'supervisor_pid': fields.String(
            required=True,
            description='The PID of the supervisord process'
        )
    }))
})

"""
Node DTO
"""

# https://realpython.com/python-data-classes/
# https://www.python.org/dev/peps/pep-0557/
@dataclass(frozen=True)
class DockerInfoDTO:
    """ Node Docker info """
    
    hostname: str
    image: str
    tag: str
    ip: str = ''

def default_supervisor_state():
    return {
        'name': '',
        'code': ''
    }

@dataclass(frozen=True)
class SupervisordInfoDTO:
    """ Node Supervisord info """

    port: str = ''
    username: str = ''
    password: str = ''
    log_level: str = ''
    api_protocol: str = ''
    api_version: str = ''
    supervisor_version: str = ''
    supervisor_id: str = ''
    supervisor_state: Dict = field(default_factory=default_supervisor_state)
    supervisor_pid: str = ''

@dataclass(frozen=True)
class ToskoseNodeInfoDTO:
    """ Info about a Toskose Node (DTO) """

    node_id: str
    hosted_components: List
    reachable: bool
    standalone: bool
    docker: DockerInfoDTO
    supervisord: SupervisordInfoDTO

"""
Hosted Component Schema
"""

hosted_component_info = ns_toskose_node.model('HostedComponentInfo', {
    'component_id': fields.String(
        required=True,
        description='The identifier of the hosted component'
    ),
    'lifecycle_operations': fields.List(
        fields.String,
        required=True,
        description='The list of lifecycle operations available'
    )
})

"""
Hosted Component DTO
"""

@dataclass(frozen=True)
class HostedComponentInfoDTO:
    """ Info about a Hosted Component (DTO) """
    component_id: str
    #current_state: str # TODO current state in the model (?)
    lifecycle_operations: List

"""
Lifecycle Operation Schema
"""

lifecycle_operation_info = ns_toskose_node.model('LifecycleOperationInfo', {
    'node_id': fields.String(
        required=True,
        description='The identifier of the node.'
    ),
    'component_id': fields.String(
        required=True,
        description='The identifier of the hosted component.'
    ),
    'operation': fields.String(
        required=True,
        description='The lifecycle operation executed on the component.'
    ),
    'description': fields.String(
        required=True,
        description='A description about the current state of the lifecycle operation. \
        If the state is RUNNING, then process_id and the uptime is shown. \
        If the state is STOPPED, then the stop time is shown (e.g. Jun 5 03:16 PM). \
        Otherwise, a generic description about the state is shown (e.g. Not Started).'
    ),
    'time_start': fields.String(
        required=True,
        description='the timestamp of when the lifecycle operation was started or 0 if \
        the lifecycle operation has never beeen started.'
    ),
    'time_end': fields.String(
        required=True,
        description='The timestamp of when the lifecycle operation last endend or 0 if \
        the lifecycle operation has never been stopped.'
    ),
    'uptime': fields.String(
        required=True,
        description='The uptime of the lifecycle operation or 0 if the lifecycle \
        operation has never been started.'
    ),
    'state_code': fields.String(
        required=True,
        description='The code of the state of the lifecycle operation. \
        The possible codes are: \n \
        - 0: STOPPED \n \
        - 10: STARTING \n \
        - 20: RUNNING \n \
        - 30: BACKOFF \n \
        - 40: STOPPING \n \
        - 100: EXITED \n \
        - 200: FATAL \n \
        - 1000: UNKNOWN'
    ),
    'state_name': fields.String(
        required=True,
        description='The state of the lifecycle operation. The possible states are: \n \
        - STOPPED: The lifecycle operation has been stopped due to a stop request or has \
        never been started. \n \
        - STARTING: The lifecycle operation is starting due to a start request. \n \
        - RUNNING: The lifecycle operation is running. \n \
        - BACKOFF: The lifecycle operation entered the STARTING state but subsequently \
        exited too quickly to move to the RUNNING state. \n \
        - STOPPING: The lifecycle operation is stopping due to a stop request. \n \
        - EXITED: The lifecycle operation exited from the RUNNING state (expectedly or \
        unexpectedly). \n \
        - FATAL: The lifecycle operation could not be started successfully. \n \
        - UNKNOWN: The lifecycle operation is in an unknown state.'
    ),
    'logfile_path': fields.String(
        required=False,
        description='Alias for stdout_logfile_path. Only for Supervisor 2.x \
        compatibility. (Deprecated)'
    ),
    'stdout_logfile_path': fields.String(
        required=True,
        description='The absolute path and the filename of the STDOUT logfile'
    ),
    'stderr_logfile_path': fields.String(
        required=True,
        description='The absolute path and the filename of the STDERR logfile. \
        It can be empty if the stderr redirection option is activated.'
    ),
    'spawn_error': fields.String(
        required=True,
        description='The description of the error that occurred during spawn or \
        an empty string if none error occurred.'
    ),
    'exit_status': fields.String(
        required=True,
        description='The exit status of the lifecycle operation (ERROR LEVEL) or 0 if \
        the process is still running.'
    ),
    'pid': fields.String(
        required=True,
        description='The UNIX Process ID (PID) of the lifecycle operation or 0 if the \
        subprocess is not running.'
    )
})

multi_lifecycle_operation_result = ns_toskose_node.model('LifecycleOperationResult', {
    'name': fields.String(
        required=True,
        description='The name of the lifecycle operations.'
    ),
    'group': fields.String(
        required=True,
        description='The name of the lifecycle operations\'s group.'
    ),
    'status_code': fields.String(
        required=True,
        description='The status code returned for the operation.'
    ),
    'description': fields.String(
        required=True,
        description='A description about the operation\' result.'
    )
})

"""
Lifecycle Operation DTO
"""
@dataclass(frozen=True)
class LifecycleOperationInfoDTO:
    node_id: str
    component_id: str
    operation: str
    description: str
    time_start: str
    time_end: str
    uptime: str
    state_code: str
    state_name: str
    logfile_path: str
    stdout_logfile_path: str
    stderr_logfile_path: str
    spawn_error: str
    exit_status: str
    pid: str


@dataclass(frozen=True)
class SubprocessOperationResultDTO:
    name: str
    group: str
    status_code: str
    description: str
