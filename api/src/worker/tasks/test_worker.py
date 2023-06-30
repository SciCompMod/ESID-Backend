from app import celery_app, logger
logger.error("Hey")

def hello_world(**kwargs):
    logger.error("----------------------------------")
    logger.error(kwargs)
    return f"Hello World! \n {str(kwargs)}"


@celery_app.task(name='test_worker')
def test_worker(**message):
    logger.error("----------------------------------")
    logger.error(message)
    return hello_world(**message)
