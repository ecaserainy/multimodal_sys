from celery import shared_task
from services.multimodal_manager import MultimodalManager
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
manager = MultimodalManager(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

@shared_task
def multimodal_inference_task(task_data: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(manager.process_task(task_data))
    return result
