import os
import shutil
import socket
import sys
import tempfile
import copy
from distutils.dir_util import copy_tree
from enum import Enum, auto

from yaml.tokens import DirectiveToken

from app.client.client import ProtocolType, ToskoseClientFactory
from app.config import AppConfig, ToskoseConfig
from app.core.commons import CommonErrorMessages
from app.core.exceptions import (ConfigurationError, FatalError, ClientConnectionError,
                                 MalformedConfigurationError, ValidationError,
                                 ResourceNotFoundError)
from app.core.loader import Loader
from app.core.logging import LoggingFacility
from app.tosca.parser import ToscaParser
from app.tosca.model.artifacts import ToskosedImage
from app.validation import validate_configuration


logger = LoggingFacility.get_instance().get_logger()


SUPPORTED_CONFIGURATION_EXTENSIONS = ['.YAML', '.YML']


class ConfigType(Enum):
    TOSKOSE_CONFIG = 'config'
    TOSCA_MANIFEST = 'manifest'

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
        self._model = None

        self.initialization()

    # def initializer(func):
    #     def wrapper(self, *args, **kwargs):
    #         if self.config is None or self.model is None:
    #             logger.debug('Loading the configuration files..')
    #             self.initialization()
    #         return func(self, *args, **kwargs)
    #     return wrapper
                    
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

    def _load(self, config_type, config_dir=None, config_name=None):
        """ Load a configuration file """

        if config_dir is None:
            if config_type == ConfigType.TOSKOSE_CONFIG:
                config_dir = ToskoseConfig.APP_CONFIG_PATH
            elif config_type == ConfigType.TOSCA_MANIFEST:
                config_dir = ToskoseConfig.APP_MANIFEST_PATH
            else:
                raise ValueError('invalid config type {}'.format(config_type.value))

        if not os.path.exists(config_dir):
            raise FatalError('The dir {} doesn\'t exist.'.format(config_dir))

        with tempfile.TemporaryDirectory() as tmp_dir:
            shutil.copytree(config_dir, os.path.join(tmp_dir, config_type.value))
            config_dir = os.path.join(tmp_dir, os.path.basename(config_dir))
            config_path = ToskoseManager._load_configurations(config_dir, config_name)

            try:
                # workaround
                # inside the manifest path there is the "imports" subdir containing
                # all the imports described in the section "imports" of the tosca manifest
                # toscaparser want imports and manifest in the same folder for building the model.
                if config_type == ConfigType.TOSCA_MANIFEST:
                    ToskoseManager._merge_imports(config_dir)
                    return ToscaParser().build_model(config_path) # also make validation

                return validate_configuration(self._loader.load(config_path))

            except (ValidationError, MalformedConfigurationError) as err:
                logger.warn('An error is occurred during the validation of {}'.format(config_path))
                raise ConfigurationError('The configuration {} is invalid or corrupted'.format(
                    os.path.basename(config_path))) from err

    def update_model(self):
        for container in self._model.containers:
            for node_id, node_data in self._config['nodes'].items():
                if container.name == node_id:
                    for data_key, data_value in node_data.items():
                        if 'docker' in data_key:
                            container.add_artifact(ToskosedImage(
                                data_value['name'],
                                data_value['tag']
                            ))
                        else:
                            setattr(container, data_key, data_value)
                            # TODO update model with associated fields
                            # TODO ensure the config/model validation
                            # TODO ensure that config has exactly the fields
                            # that are also in the model (no additional)
                            # hope that the jsonschema in toskose tool is
                            # working well, maybe :|

    def initialization(self):
        """ Initialization
        
        - Loading configuration files
        - Updating the TOSCA model representation
        """

        self._config = self._load(ConfigType.TOSKOSE_CONFIG)
        self._model = self._load(ConfigType.TOSCA_MANIFEST)
        self.update_model()

    def validation(func):
        def wrapper(self, *args, **kwargs):
            if args[0] not in self._config['nodes']:
                raise ResourceNotFoundError('node {} not exist'.format(args[0]))
            return func(self, *args, **kwargs)
        return wrapper

    @property
    def nodes(self):
        return self._model.containers

    @validation
    def node_by_id(self, node_id):
        for container in self._model.containers:
            if container.name == node_id:
                return container

    @validation
    def get_client(self, node_id):

        logger.debug('Requested client instance for node [{}]'.format(node_id))
        node_config = self._config['nodes'][node_id]

        # check if it's a standalone container (no supervisord logic)
        # for container in self.nodes:
        #     if container.name == node_id and not container.hosted:
        #         logger.debug('Detected a standalone node container [{}]'.format(node_id))
        #         return ToskoseClientFactory.create(
        #             protocol_type=ProtocolType.DOCKER.name,
        #             hostname=node_config['hostname']
        #         )

        return ToskoseClientFactory.create(
            protocol_type=AppConfig._CLIENT_PROTOCOL,
            hostname=node_config['hostname'],
            port=node_config['port'],
            username=node_config['user'],
            password=node_config['password'],
        )