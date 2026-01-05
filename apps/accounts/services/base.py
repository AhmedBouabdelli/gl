from django.db import transaction
from logging import getLogger

logger = getLogger(__name__)


class BaseService:
    """Base service class with common utilities"""

    @staticmethod
    def log_info(message):
        """Log info message"""
        logger.info(message)

    @staticmethod
    def log_warning(message):
        """Log warning message"""
        logger.warning(message)

    @staticmethod
    def log_error(message, exception=None):
        """Log error message"""
        if exception:
            logger.error(f'{message}: {str(exception)}')
        else:
            logger.error(message)
