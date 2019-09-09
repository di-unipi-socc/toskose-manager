import socket

from abc import ABC, abstractmethod
from typing import List, Dict

from app.core.logging import LoggingFacility
from app.core.exceptions import ClientConnectionError


logger = LoggingFacility.get_instance().get_logger()


class BaseClient(ABC):

    def __init__(self, hostname=None, port=None, username=None, password=None):
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password

    @property
    def hostname(self):
        return self._hostname

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def ipv4(self):
        try:
            return socket.gethostbyname(self.hostname)
        except socket.error:
            logger.warn('Failed to resolve hostname [{}]'.format(self.hostname))
            raise ClientConnectionError('Connection failed')

    @abstractmethod
    def reachable(self) -> bool:
        """ Check if the destination is reachable.
        
        Returns:
            bool: True if is reachable, False, otherwise.
        """