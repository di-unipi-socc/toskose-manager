import os
import sys
import socket
import shutil
import tempfile
from distutils.dir_util import copy_tree

from app.config import AppConfig, ToskoseConfig
from app.client.client import ToskoseClientFactory, ProtocolType
from app.core.logging import LoggingFacility
from app.core.loader import Loader
from app.core.exceptions import ValidationError, MalformedConfigurationError, \
                                FatalError, ConfigurationError
from app.validation import validate_configuration
from app.tosca.parser import ToscaParser
from app.core.commons import CommonErrorMessages


logger = LoggingFacility.get_instance().get_logger()


SUPPORTED_CONFIGURATION_EXTENSIONS = ['.YAML', '.YML']


class ToskoseManager():
    """ A singleton containing the application settings """
    __instance = None

    @staticmethod
    def get_instance():
        """ The static access method """

        if ToskoseManager.__instance == None:
            ToskoseManager()

        return ToskoseManager.__instance

    def __init__(self):
        if ToskoseManager.__instance != None:
            raise Exception('This is a singleton')
        else:
            ToskoseManager.__instance = self

        self._loader = Loader()
        self._config = None
        self._manifest = None
        self._model = None

    def config_loader(func):
        def wrapper(self, *args, **kwargs):
            if self._config is None or \
                self._manifest is None or \
                self._model is None:
                self.load()
            return func(self, *args, **kwargs)
        return wrapper
                    
    @staticmethod
    def _load_configurations(config_dir, config_name=None):

        if config_name is None:
            configs = []
            for fname in os.listdir(config_dir):
                path = os.path.join(config_dir, fname)
                if os.path.isdir(path):
                    continue # skip dirs
                if fname.upper().endswith(tuple(SUPPORTED_CONFIGURATION_EXTENSIONS)):
                    configs.append(fname)

            if len(configs) > 1:
                logger.warn('Multiple configurations detected in {}'.format(config_dir))
                logger.warn('No configuration specified, selected the first one {}'.format(configs[0]))
            elif len(configs) == 1:
                logger.info('Detected configuration {}'.format(fname))
            else:
                logger.error('No configurations detected. Abort.')
                raise FatalError('A fatal error is occurred. See logs for further details.')

            config_path = os.path.join(config_dir, configs[0])

        else:
            config_path = os.path.join(config_dir, config_name)
            if not os.path.exists(config_path):
                raise ValueError('Configuration {} doesnt exists'.format(config_path))

        return config_path

    def _cross_validation(config, manifest):
        """ Validate the configuration file against the TOSCA model. 
        
        e.g. check if the nodes are the same
        """
        pass
        # TODO

    def _merge_imports(manifest_dir):
        
        imports_dir = os.path.join(manifest_dir, 'imports')
        if not os.path.exists(imports_dir):
            raise FatalError('missing tosca imports dir')

        for file in os.listdir(imports_dir):
            shutil.move(os.path.join(imports_dir, file), manifest_dir)

        shutil.rmtree(imports_dir, ignore_errors=True)
        
    def load(self, config_dir=None, config_name=None, manifest_dir=None, manifest_name=None):
        """ Load the configuration files. """

        if config_dir is None:
            config_dir = ToskoseConfig.APP_CONFIG_PATH
        if manifest_dir is None:
            manifest_dir = ToskoseConfig.APP_MANIFEST_PATH

        if not os.path.exists(config_dir):
            raise FatalError('The dir {} containing toskose config files doesn\'t exist.'.format(config_dir))
        if not os.path.exists(manifest_dir):
            raise FatalError('The dir {} containing tosca manifest files doesn\' exists.'.format(manifest_dir))
        
        try:

            with tempfile.TemporaryDirectory() as tmp_dir:

                shutil.copytree(config_dir, os.path.join(tmp_dir, 'config'))
                shutil.copytree(manifest_dir, os.path.join(tmp_dir, 'manifest'))

                config_dir = os.path.join(tmp_dir, os.path.basename(config_dir))
                manifest_dir = os.path.join(tmp_dir, os.path.basename(manifest_dir))

                config_path = ToskoseManager._load_configurations(config_dir, config_name)
                manifest_path = ToskoseManager._load_configurations(manifest_dir, manifest_name)

                self._config = validate_configuration(self._loader.load(config_path))
                self._manifest = manifest_path # TODO validation

                # workaround
                # inside the manifest path there is the "imports" subdir containing
                # all the imports described in the section "imports" of the tosca manifest
                # toscaparser want imports and manifest in the same folder for building the model.
                ToskoseManager._merge_imports(manifest_dir)

                self._model = ToscaParser().build_model(manifest_path)
                ToskoseManager._cross_validation(self._config, self._model)
        except (ValidationError, MalformedConfigurationError) as err:
            # re-raise to send error through the API
            if self._config is None:
                msg = 'The configuration file {} is invalid or corrupted'.format(
                    os.path.basename(config_path))
            if self._manifest is None:
                msg = 'The TOSCA manifest file {} is invalid or corrupted'.format(
                    os.path.basename(manifest_path))
            self.close()
            raise ConfigurationError(msg)
        
    @property
    @config_loader
    def nodes(self):
        return self._config['nodes']

    @config_loader
    def get_client(self, node_id):

        if node_id not in self._config['nodes']:
            raise ValueError('node {} not exist'.format(node_id))

        logger.debug('Requested client instance for node [{}]'.format(node_id))
        node_config = self.nodes[node_id]

        hostname = node_config['hostname']
        try:
            hostname = socket.gethostbyname(hostname)
        except Exception as err:
            logger.warn('Failed to resolve hostname for node {}. Trying localhost..'.format(node_id))
            hostname = '127.0.0.1'
        logger.debug('The hostname for the node {0} is {1}'.format(node_id, hostname))

        # check if it's a standalone container (no supervisord logic)
        standalone = False
        for container in self._model.containers:
            if container.name == node_id and not container.hosted:
                standalone = True
                logger.debug('Detected a standalone node container [{}]'.format(node_id))
                return ToskoseClientFactory.create(
                    protocol_type=ProtocolType.DOCKER.name,
                    hostname=hostname
                )

        return ToskoseClientFactory.create(
            protocol_type=AppConfig._CLIENT_PROTOCOL,
            hostname=node_config['hostname'],
            port=node_config['port'],
            username=node_config['user'],
            password=node_config['password'],
        )

    @config_loader
    def get_node_data(self, *, node_id=None, hostname=None, port=None):
        """ returns the configuration file data associated to the node

        data can be obtained by node_id or by hostname and port of the node.

        Args:
            node_id (str): the node identifier.
            hostname (str): the node\'s hostname.
            port (str): the node\'s port.

        Returns:
            result: a tuple (node_id, node_data) containing the node identifier
            and the node\'s data associated.

        """

        if not node_id:
            if not hostname or not port:
                raise ValueError('hostname and port must be given')
            else:
                for node_id, node_data in self.nodes.items():
                    if node_data.get('hostname') == hostname and \
                        node_data.get('port') == port:
                        return node_id, node_data
                raise FatalError('no data for the node {0}' \
                    .format(node_id))

        node_data = self.nodes.get(node_id)
        if not node_data:
            raise FatalError('node {0} not found' \
                .format(node_id))
        return node_id, node_data

    def close(self):
        shutil.rmtree(self._tmp_dir)