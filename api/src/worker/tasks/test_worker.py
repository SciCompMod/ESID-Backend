from app import celery_app, logger

def hello_world(**kwargs):
    logger.info("----------------------------------")
    logger.info(kwargs)
    return f"Hello World! \n {str(kwargs)}"


@celery_app.task(name='test_worker')
def test_worker(**message):
    logger.info("----------------------------------")
    logger.info(message)
    return hello_world(**message)
