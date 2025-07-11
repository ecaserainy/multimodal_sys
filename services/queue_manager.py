import redis,os,json

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)

task_queues = {
    "text": "text_task_queue",
    "image": "image_task_queue",
    "audio": "audio_task_queue",
}

result_queue = "task_result_queue"

def push_task(task_type, task_data):
    queue = task_queues.get(task_type)
    if queue:
        redis_client.rpush(queue, json.dumps(task_data))

def pop_text_task():
    return _pop_task(task_queues["text"])

def pop_image_task():
    return _pop_task(task_queues["image"])

def pop_audio_task():
    return _pop_task(task_queues["audio"])

def push_task_result(task_id, result):
    redis_client.hset(result_queue, task_id, json.dumps(result))

def get_task_result(task_id):
    result = redis_client.hget(result_queue, task_id)
    return json.loads(result) if result else None

def _pop_task(queue_name):
    task_data = redis_client.lpop(queue_name)
    return json.loads(task_data) if task_data else None























# import asyncio
# from services.cache import redis_client
# from services.multimodal_manager import MultimodalManager
#
# multimodal_manager = MultimodalManager()
#
# async def worker():
#     print("[Worker] Starting async worker...")
#     while True:
#         task = await redis_client.blpop("multimodal_queue", timeout=5)
#         if not task:
#             await asyncio.sleep(1)
#             continue
#
#         _, task_data = task
#         task_obj = json.loads(task_data)
#
#         task_id = task_obj["task_id"]
#         inputs = task_obj["input"]
#
#         print(f"[Worker] Processing task {task_id}")
#
#         try:
#             result = await multimodal_manager.process_task(inputs)
#         except Exception as e:
#             print(f"[Worker] Task {task_id} error: {e}")
#             result = {"error": str(e)}
#
#         await redis_client.set(f"multimodal_result:{task_id}", json.dumps(result), ex=300)
#         print(f"[Worker] Task {task_id} done")
