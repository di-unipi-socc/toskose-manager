import os
import ruamel.yaml

from app.core.logging import LoggingFacility
from app.core.exceptions import ValidationError
from app.core.exceptions import MalformedConfigurationError


logger = LoggingFacility.get_instance().get_logger()


class Loader:
    def __init__(self):
        pass

    def load(self, path, **kwargs):
        """ Load the configuration from a given file. """

        if not os.path.exists(path):
            raise ValueError('The given path {} doesn\'t exists.'.format(path))

        logger.debug('Loading data from {}'.format(path))
        try:
            with open(path, 'r') as f:
                return ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
        except ruamel.yaml.error.YAMLError as err:
            logger.exception('Failed to load {}'.format(path))
            raise MalformedConfigurationError(os.path.basename(path)) from err