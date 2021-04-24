"""
Celery Config File for Bot Server
"""

result_backend = 'redis://localhost:6379/0'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
task_time_limit = 420
task_soft_time_limit = 360
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 6