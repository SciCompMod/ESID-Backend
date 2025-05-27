from app import celery_app, logger

@celery_app.task(name='tasks.test_worker', bind=True)
def test_worker(self, **kwargs):
    logger.info("-- Task --")
    logger.info(kwargs)
    return True
