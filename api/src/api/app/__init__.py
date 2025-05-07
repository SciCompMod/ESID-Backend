from celery import Celery
from core import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


celery_app = Celery(
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    broker_connection_max_retries=30,
    include=["tasks"],
)
celery_app.config_from_object("celery_app_config")


def create_app():
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)
    origins = ["http://localhost", "http://localhost:8000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from app import routers

    routers.init_app(app)
    return app
