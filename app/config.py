import os
import sys
import app


DEFAULT_FLASK_SECRET_KEY = 'to-iterate-is-human-to-recurse-divine'

DEFAULT_CONFIG_PATH = '/toskose/config'
DEFAULT_MANIFEST_PATH = '/toskose/manifest'
DEFAULT_LOGS_PATH = '/logs/toskose'
DEFAULT_APP_VERSION = '{}-dev'.format(app.__version__)
DEFAULT_APP_MODE = 'development'

DEFAULT_CLIENT_PROTOCOL = 'XMLRPC'


class AppConfig(object):
    """ Application Configuration

    _CLIENT_PROTOCOL: the client protocol used to communicate with the Supervisord instances
    _LOGS_FILE_NAME: the name of the Toskose Manager's log file
    _LOGS_PATH: the absolute path of the Toskose Manager's log file
    _APP_CONFIG_NAME: the name of the Toskose Manager's configuration file
    _APP_CONFIG_PATH: the absolute path of the Toskose Manager's configuration file
    _APP_MODE: the execution configuration of Toskose Manager (development|testing|production)
    _APP_VERSION: the version of Toskose Manager (will be visualized in the API Documentation)
    """

    _CLIENT_PROTOCOL = os.environ.get('TOSKOSE_CLIENT_PROTOCOL', DEFAULT_CLIENT_PROTOCOL)

    _LOGS_CONFIG_NAME = 'logging.conf'
    _LOGS_PATH = os.environ.get('TOSKOSE_LOGS_PATH', DEFAULT_LOGS_PATH)

    _APP_MODE = os.environ.get('TOSKOSE_APP_MODE', DEFAULT_APP_MODE)
    _APP_VERSION = os.environ.get('TOSKOSE_APP_VERSION', DEFAULT_APP_VERSION)

class ToskoseConfig(object):
    """ TOSCA Configuration 
    
    """
    
    APP_CONFIG_PATH = os.environ.get('TOSKOSE_CONFIG_PATH', DEFAULT_CONFIG_PATH)
    APP_MANIFEST_PATH = os.environ.get('TOSKOSE_MANIFEST_PATH', DEFAULT_MANIFEST_PATH)


class FlaskConfig(object):
    """ Flask Configuration

    SECRET_KEY: used to sign cookies and other things (**important)
    DEBUG: activate the debugging mode (e.g. unhandled exceptions, reloading
    server when code changes). It is overridden by FLASK_DEBUG env.
    ERROR_404_HELP: disable the automagically hint on 404 response messages
    """

    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_FLASK_SECRET_KEY)
    DEBUG = False
    TESTING = False
    ERROR_404_HELP = False


class DevelopmentConfig(FlaskConfig):
    """ Flask Development Configuration """

    DEBUG = True


class TestingConfig(FlaskConfig):
    """ Flask Testing Configuration """

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class ProductionConfig(FlaskConfig):
    """ Flask Production Configuration """
    pass

configs = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)
