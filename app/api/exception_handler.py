from app.api import api

from app.core.exceptions import FatalError, ClientFatalError, ResourceNotFoundError, \
                                ClientOperationFailedError, ClientConnectionError, \
                                OperationNotValid, ConfigurationError, ParsingError, \
                                ValidationError, MalformedConfigurationError

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