"""
Provides a Celery instance integrated with Flask
"""

from celery import Celery
import bot_config


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=bot_config.CELERY_RESULT_BACKEND,
        broker=bot_config.CELERY_BROKER_URL
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
