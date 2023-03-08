import logging

from celery import Celery
from core import config
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    broker_connection_max_retries=30,
    include=["tasks"],
)
celery_app.config_from_object("celery_app_config")

c_logger = logging.getLogger("celery")

c_logger.setLevel(logging.INFO)


def _create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger


logger = _create_logger()
