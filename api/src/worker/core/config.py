from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")
PROJECT_NAME = "Pandemos Interface"
VERSION = "0.0.1"

SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")

CELERY_BROKER_URL = config("CELERY_BROKER_URL", cast=str, default="redis://redis:6379")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", cast=str, default="redis://redis:6379")
