import time
from services.queue_manager import pop_text_task, push_task_result
from services.di import container
from app.models.text_model import run_text_inference

def start_text_worker():
    print("[TextWorker] Starting...")
    while True:
        task = pop_text_task()
        if task:
            model = container.text_model
            result = run_text_inference(model, task["content"])
            push_task_result(task["task_id"], result)
        else:
            time.sleep(0.5)