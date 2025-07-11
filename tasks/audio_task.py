from celery import shared_task
from services.di import container
from app.models.audio_model import run_audio_inference

@shared_task
def audio_inference_task(audio_path: str):
    model = container.audio_model
    return run_audio_inference(model, audio_path)


