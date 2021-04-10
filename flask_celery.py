from celery import Celery
import config


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=config.CELERY_RESULT_BACKEND,
        broker=config.CELERY_BROKER_URL
    )
    print('Celery app created')
    celery.conf.update(app.celery_config)
    print('Config read successfully')
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
