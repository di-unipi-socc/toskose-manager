from abc import ABC, abstractmethod
from typing import List, Dict


class BaseClient(ABC):

    def __init__(self, host, port=None, username=None, password=None, standalone=False):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._standalone = standalone

    @property
    def host(self):
        return self._host

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
    def standalone(self):
        return self._standalone

    @abstractmethod
    def is_reacheable(self) -> bool:
        """ Check if the destination is reachable.
        
        Returns:
            bool: True if is reachable, False, otherwise.
        """