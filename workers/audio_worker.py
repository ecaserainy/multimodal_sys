import time
from services.queue_manager import pop_audio_task, push_task_result
from services.di import container
from app.models.audio_model import run_audio_inference

def start_audio_worker():
    print("[AudioWorker] Starting...")
    while True:
        task = pop_audio_task()
        if task:
            model = container.audio_model
            result = run_audio_inference(model, task["audio_path"])
            push_task_result(task["task_id"], result)
        else:
            time.sleep(0.5)