from celery import Celery
from celery.schedules import crontab
from src.fast_api_airguardian.settings  import settings


celery_app = Celery(
    "nfz_monitor",
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    imports=['src.fast_api_airguardian.task']
)

celery_app.conf.beat_schedule = {
    'fetch-drone-positions-every-10s' : {
        'task': 'src.fast_api_airguardian.tasks.fetch_drone_positions_task',
        'schedule': 10.0,
    },
}