from celery import shared_task
import asyncio
from services.di import get_container


@shared_task
def multimodal_agent_inference_task(task_data: dict):
    manager = get_container().multimodal_manager
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(manager.run_agent(task_data))
    loop.close()
    return result