from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "aios_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    # Crucial: Register tasks directory to ensure handlers are visible
    include=["app.tasks.task_handlers"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Priority for enterprise robustness
    task_track_started=True,
    task_time_limit=3600, # 1 hour max execution
)
