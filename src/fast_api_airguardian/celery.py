from celery import Celery
from celery.schedules import crontab
from src.fast_api_airguardian.settings  import settings


celery_app = Celery(
    "nfz_monitor",  # airguadian
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
   # task_acks_late=True,
   #  worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    'fetch-drone-positions-every-10s' : {
        'task': 'src.fast_api_airguardian.tasks.fetch_drone_positions_task',
        'schedule': 10.0,
    },
}

# Import tasks here so Celery registers them
celery_app.autodiscover_tasks(['src.fast_api_airguardian'])
from src.fast_api_airguardian import task
