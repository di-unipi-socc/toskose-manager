from flask import Blueprint
from flask_restplus import Api
from app.config import AppConfig

from app.core.exceptions import FatalError, ClientFatalError, ResourceNotFoundError, \
                                ClientOperationFailedError, ClientConnectionError, \
                                OperationNotValid, ConfigurationError, ParsingError, \
                                ValidationError, MalformedConfigurationError


bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    bp,
    title='Toskose Manager API',
    version=AppConfig._APP_VERSION,
    description='API for managing TOSCA-based multi-component cloud applications'
)

from app.api.controllers.node_controller import ns as ns_node
api.add_namespace(ns_node, path='/node')

from app.api.controllers.subprocess_controller import ns as ns_subprocess
api.add_namespace(ns_subprocess, path='/subprocess')

# API Exceptions handlers

@api.errorhandler(FatalError)
def handle_fatal_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(ClientFatalError)
def handle_client_fatal_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(ResourceNotFoundError)
def handle_client_connection_error(error):
    return ({ 'message': '{0}'.format(error) }, 400)

@api.errorhandler(ClientOperationFailedError)
def handle_client_protocol_error(error):
    return ({ 'message': '{0}'.format(error) }, 400)

@api.errorhandler(ClientConnectionError)
def handle_client_connection_error(error):
    return ({ 'message': '{0}'.format(error) }, 404)

@api.errorhandler(OperationNotValid)
def handle_operation_not_valid(error):
    return ({ 'message': '{0}'.format(error) }, 400)

@api.errorhandler(ConfigurationError)
def handle_configuration_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(ParsingError)
def handle_parsing_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(MalformedConfigurationError)
def handle_malformed_configuration_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)
