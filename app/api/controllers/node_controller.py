from flask_restplus import Namespace, Resource, fields, inputs, reqparse

from app.api.services.node_service import LifecycleOperationActionType
from app.api.models import (hosted_component_info, lifecycle_operation_info,
                            multi_lifecycle_operation_result)
from app.api.models import ns_toskose_node as ns
from app.api.models import toskose_node_info
from app.api.services.node_service import (LifecycleOperationActionType,
                                           LogsActionType, NodeService)

node_service = NodeService()


@ns.header('Content-Type', 'application/json')
class NodeOperation(Resource):
    """ Base class for common configurations """
    
@ns.route('/')
class ToskoseNodeList(NodeOperation):
    
    @ns.marshal_list_with(toskose_node_info)
    def get(self):
        """ The list of nodes info """
        return NodeService().get_all_nodes_info()

@ns.route('/reload')
class ToskoseManagerReload(NodeOperation):

    def post(self):
        """ Re-initialize the manager """
        return 'OK' if node_service.reload() \
            else ns.abort(500, message='failed to reload the manager')

@ns.route('/<string:node_id>')
@ns.param('node_id', 'the node identifier')
class ToskoseNode(NodeOperation):
    """ Manage a node lifecycle """
    
    @ns.marshal_with(toskose_node_info)
    def get(self, node_id):
        """ The current state of a node """
        return NodeService().node_info(node_id=node_id)        

@ns.route('/<string:node_id>/operations')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeOperations(NodeOperation):
    """ Manage all the lifecycle operations in the node """

    @ns.marshal_list_with(multi_lifecycle_operation_result)
    def delete(self, **kwargs):
        """ Stop all running lifecycle operations """
        return node_service.stop_all_operations(**kwargs)

node_log_parser = reqparse.RequestParser()
node_log_parser.add_argument('offset', type=int, required=False,
    default=0)
node_log_parser.add_argument('length', type=int, required=False,
    default=0)

@ns.route('/<string:node_id>/log')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeLog(NodeOperation):
    """ Manage the logs of a node. """

    @ns.expect(node_log_parser, validate=True)
    def get(self, **kwargs):
        """ Fetch the log of a node """

        log = node_service.node_logs(
            action=LogsActionType.READ, 
            offset=node_log_parser.parse_args()['offset'],
            length=node_log_parser.parse_args()['length'],
            **kwargs)
        return log if log else ns.abort(500, message='failed to fetch the log')

    def delete(self, **kwargs):
        """ Clear the log of a node """
        
        return 'OK' if node_service.node_logs(
            action=LogsActionType.CLEAR,
            **kwargs) \
            else ns.abort(500, message='failed to clear the log')


@ns.route('/<string:node_id>/<string:component_id>')
@ns.param('component_id', 'the hosted component identifier')
@ns.param('node_id', 'the node identifier')
class ComponentLifecycleOperationList(NodeOperation):
    """ The list of lifecycle operations of an hosted component. """

    @ns.marshal_with(hosted_component_info)
    def get(self, **kwargs):
        """ Info about a hosted component """
        return node_service.hosted_component_info(**kwargs)

@ns.route('/<string:node_id>/<string:component_id>/<string:operation>')
@ns.param('operation', 'the lifecycle operation')
@ns.param('component_id', 'the hosted component identifier')
@ns.param('node_id', 'the node identifier')
class ComponentLifecycleOperation(NodeOperation):
    """ Manage lifecycle operations on a component hosted on a node. """

    @ns.marshal_with(lifecycle_operation_info)
    def get(self, **kwargs):
        """ Info about the status of a lifecycle operation. """

        return node_service.execute(
            action=LifecycleOperationActionType.INFO,
            **kwargs)
    
    def post(self, **kwargs):
        """ Start a lifecycle operation. """

        return 'OK' if node_service.execute(
            action=LifecycleOperationActionType.START,
            **kwargs) \
            else ns.abort(500, message='failed to start operation')

    def delete(self, **kwargs):
        """ Stop a lifecycle operation. """

        return 'OK' if node_service.execute(
            action=LifecycleOperationActionType.STOP,
            **kwargs) \
            else ns.abort(500, message='failed to stop operation')

operation_signal_parser = reqparse.RequestParser() \
    .add_argument('signal_type', type=str, required=True,
        default='SIGTERM',
        help='the signal type')

@ns.route('/<string:node_id>/<string:component_id>/<string:operation>/signal')
@ns.param('operation', 'the lifecycle operation')
@ns.param('component_id', 'the hosted component identifier')
@ns.param('node_id', 'the node identifier')
class ComponentLifecycleOperationSignal(NodeOperation):
    """ Send a custom signal to a lifecycle operation. """

    @ns.expect(operation_signal_parser, validate=True)
    def post(self, **kwargs):
        """ Signal a lifecycle operation. """

        return 'OK' if node_service.execute(
            action=LifecycleOperationActionType.SIGNAL,
            signal=operation_signal_parser.parse_args()['signal_type'],
            **kwargs) \
            else ns.abort(500, message='failed to signal operation')

# note: type=bool with Python default bool class not working
# use inputs.boolean from restplus library instead
operation_log_parser = reqparse.RequestParser() \
    .add_argument('tail', type=inputs.boolean, required=False,
        default=False, help='set true for tailing the log') \
    .add_argument('std_type', type=str, required=True,
        choices=['stdout', 'stderr'], default='stdout',
        help='the std we read from') \
    .add_argument('offset', type=int, required=False,
        default=0) \
    .add_argument('length', type=int, required=False,
        default=0)

@ns.route('/<string:node_id>/<string:component_id>/<string:operation>/log')
@ns.param('operation', 'the lifecycle operation')
@ns.param('component_id', 'the hosted component identifier')
@ns.param('node_id', 'the node identifier')
class ComponentLifecycleOperationLog(NodeOperation):
    """ Manage the logs of a lifecycle operation. """

    @ns.expect(operation_log_parser, validate=True)
    def get(self, **kwargs):
        """ Fetch the log of a lifecycle operation """

        is_tailing = operation_log_parser.parse_args()['tail']
        action = LogsActionType.TAIL if is_tailing else LogsActionType.READ

        log = node_service.operation_logs(
            action=action, 
            std_type=operation_log_parser.parse_args()['std_type'],
            offset=operation_log_parser.parse_args()['offset'],
            length=operation_log_parser.parse_args()['length'],
            **kwargs)
        return log if log else ns.abort(500, message='failed to fetch the log')
    
    def delete(self, **kwargs):
        """ Clear the log of a lifecycle operation """

        return 'OK' if node_service.operation_logs(
            action=LogsActionType.CLEAR,
            **kwargs) \
            else ns.abort(500, message='failed to clear the log')