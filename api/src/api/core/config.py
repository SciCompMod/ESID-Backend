from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret, URL

config = Config(".env")

PROJECT_NAME = "ESID Backend Interface"
VERSION = "2.0.0"
API_PATH_PREFIX = config("API_PATH_PREFIX", cast=str, default="")

SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")

CELERY_BROKER_URL = config("CELERY_BROKER_URL", cast=str, default="redis://redis:6379")
CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND", cast=str, default="redis://redis:6379"
)

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)

DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

# OAuth2 settings
IDP_ROOT_URL = config("IDP_ROOT_URL", cast=URL)
IDP_API_URL = config("IDP_API_URL", cast=URL)

# Forward of uploaded case file settings
UPLOAD_FORWARD_ENDPOINT = config("UPLOAD_FORWARD_ENDPOINT", cast=URL)
UPLOAD_FORWARD_ACCESS_KEY = config("UPLOAD_FORWARD_ACCESS_KEY", cast=Secret)
UPLOAD_FORWARD_SECRET_KEY = config("UPLOAD_FORWARD_SECRET_KEY", cast=Secret)
