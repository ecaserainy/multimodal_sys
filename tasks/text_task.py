from celery import shared_task
from services.di import get_container
from app.models.text_model import run_text_inference

@shared_task
def text_inference_task(content: str):
    model = get_container().text_model
    return run_text_inference(model, content)


