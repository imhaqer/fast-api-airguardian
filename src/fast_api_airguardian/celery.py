from celery import Celery
from .settings import settings


celery_app = Celery(
    "airguadian",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

@celery_app.task
def add(x, y):
    return x + y

