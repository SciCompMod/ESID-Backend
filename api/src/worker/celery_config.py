from core import config

# Broker
broker_url=config.CELERY_BROKER_URL
broker_connection_max_retries=30

# Results Backend
results_backend=config.CELERY_RESULT_BACKEND
# Keep results of task for 5 min
result_expires = 300

# Message Routing
task_default_queue = 'default'

# Worker
include=['tasks']
# dev setting to make shutdown faster
worker_lost_wait = 1

# Logging
worker_hijack_root_logger=False
