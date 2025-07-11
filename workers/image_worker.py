import time
from services.queue_manager import pop_image_task, push_task_result
from services.di import container
from app.models.image_model import run_image_inference

def start_image_worker():
    print("[ImageWorker] Starting...")
    while True:
        task = pop_image_task()
        if task:
            model = container.image_model
            result = run_image_inference(model, task["image_path"])
            push_task_result(task["task_id"], result)
        else:
            time.sleep(0.5)