class BaseError(Exception):
     
    DEFAULT_MESSAGE = 'An unknown exception occurred'

    def __init__(self, message=DEFAULT_MESSAGE):
        self.message = message

    def __str__(self):
        return self.message

class FatalError(BaseError):
    """ Raised when a fatal error is occurred. """

    def __init__(self, message):
        super().__init__(message)

class ClientFatalError(BaseError):
    """ Raised when a fatal error occurred in the client """

    def __init__(self, message):
        super().__init__(message)

class ResourceNotFoundError(BaseError):
    """ Raised when a resource cannot be found (e.g. node) """

    def __init__(self, message):
        super().__init__(message)

class ClientOperationFailedError(BaseError):
    """ Raised when an operation made by the client fails """

    def __init__(self, message):
        super().__init__(message)

class ClientConnectionError(BaseError):
    """ Raised when a communication fails """

    def __init__(self, message):
        super().__init__(message)

class OperationNotValid(BaseError):
    """ Raised when an invalid operation occurred """

    def __init__(self, message):
        super().__init__(message)

class ConfigurationError(BaseError):
    """ Raised when a configuration file is not valid. """

    def __init__(self, message):
        super().__init__(message)

class ParsingError(BaseError):
    """ Raised when an error occurred parsing a file. """

    def __init__(self, message):
        super().__init__(message)

class ValidationError(BaseError):
    """ Raised when the configuration file is not valid. """

    def __init__(self, message):
        super().__init__(message)

class MalformedConfigurationError(BaseError):
    """ Raised when the configuration file is malformed or corrupted. """

    def __init__(self, message):
        super().__init__(message)