from celery import Celery

from celery_tasks.config import BROKER_DSN

app = Celery("celery_app", broker=BROKER_DSN)
