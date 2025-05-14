from app import celery_app, logger, c_logger

def hello_world(**kwargs):
    logger.info("-- hello_world --")
    logger.info(kwargs)
    return f"Hello World! \n {str(kwargs)}"


@celery_app.task(name='tasks.test_worker', bind=True)
def test_worker(self, **kwargs):
    logger.info("-- Task --")
    logger.info(kwargs)
    return hello_world(**kwargs)
