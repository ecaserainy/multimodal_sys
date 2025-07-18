import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://192.168.1.23:6379/0")

celery_app = Celery(
    "multimodal_tasks",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    imports=["tasks.text_task", "tasks.image_task", "tasks.audio_task"],
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=False,
)
