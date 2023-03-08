from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = "Pandemos Interface"
VERSION = "0.0.1"

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

#Auth0

# DOMAIN = config("DOMAIN", cast=str, default="your.domain.com")
# API_AUDIENCE = config("API_AUDIENCE", cast=str, default="your.audience.com")
# ISSUER = config("ISSUER", cast=str, default="https://your.domain.com")
# ALGORITHMS = config("ALGORITHMS", cast=str, default="RS256")

# DOMAIN = config("DOMAIN", cast=str, default="shell-sep-dev.eu.auth0.com")
# API_AUDIENCE = config("API_AUDIENCE", cast=str, default="https://sep-backend.coacapp.de")
# ISSUER = config("ISSUER", cast=str, default="https://shell-sep-dev.eu.auth0.com/")
# ALGORITHMS = config("ALGORITHMS", cast=str, default="RS256")

DOMAIN = config("DOMAIN", cast=str, default="pandemos.eu.auth0.com")
API_AUDIENCE = config("API_AUDIENCE", cast=str, default="pandemos-api")
ISSUER = config("ISSUER", cast=str, default="https://pandemos.eu.auth0.com/")
ALGORITHMS = config("ALGORITHMS", cast=str, default="RS256")

REQUIRESAUTH = config('REQUIRESAUTH',cast=bool ,default=False)