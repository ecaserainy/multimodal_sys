from celery import shared_task
from services.di import get_container
from app.models.image_model import run_image_inference

@shared_task
def image_inference_task(image_path: str):
    model = get_container().image_model
    return run_image_inference(model, image_path)