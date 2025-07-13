from celery import shared_task
import asyncio
from services.di import get_container

manager = get_container().multimodal_manager

@shared_task
def multimodal_inference_task(task_data: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(manager.process_task(task_data))
    loop.close()
    return result