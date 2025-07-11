from celery import shared_task
import asyncio,os
from services.multimodal_manager import MultimodalManager
from dotenv import load_dotenv

load_dotenv()
manager = MultimodalManager(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

@shared_task
def multimodal_agent_inference_task(task_data: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(manager.run_agent(task_data))
    loop.close()
    return result
