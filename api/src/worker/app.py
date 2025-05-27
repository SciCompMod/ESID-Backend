import logging

from celery import Celery


celery_app = Celery()
celery_app.config_from_object('celery_config')

def _create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


logger = _create_logger()
