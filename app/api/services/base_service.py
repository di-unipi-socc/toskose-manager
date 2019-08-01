from app.core.logging import LoggingFacility
from app.manager import ToskoseManager

logger = LoggingFacility.get_instance().get_logger()

class BaseService():

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
    
    def reload(self):
        """ Re-initialize the configurations.
        
        - reload the toskose config
        - reload the TOSCA manifest
        - initialization
        """
        logger.info('Re-initialization in progress')
        ToskoseManager.get_instance().initialization()
        return True