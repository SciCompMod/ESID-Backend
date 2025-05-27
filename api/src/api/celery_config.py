from os import environ

# Broker
broker_url=environ['CELERY_BROKER_URL']
broker_connection_max_retries=30

# Results Backend
results_backend=environ['CELERY_RESULT_BACKEND']
result_expires = 120

# Message Routing
task_default_queue = 'default'

# Worker
include=['tasks']
# dev setting to make shutdown faster
worker_lost_wait = 1

# Logging
worker_hijack_root_logger=False
