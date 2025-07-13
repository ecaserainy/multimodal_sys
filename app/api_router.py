import json
import os
from typing import Optional

from celery.result import AsyncResult
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from services.di import get_container
from services.cache import redis_client
from tasks.audio_task import audio_inference_task
from tasks.image_task import image_inference_task
from tasks.multimodal_agent_task import multimodal_agent_inference_task
from tasks.text_task import text_inference_task
from utils.file_utils import BASE_UPLOAD_DIR
from services.multimodal_manager import MultimodalManager
manager = MultimodalManager()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

api_router = APIRouter()
container = get_container()
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


def success(data=None, message="success"):
    return JSONResponse(status_code=200, content={"code": 0, "message": message, "data": data})

def error(message="error", code=1, status_code=400):
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})

def save_upload_file(file: UploadFile) -> str:
    path = os.path.join(BASE_UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


# === 健康检查 ===

@api_router.get("/health")
async def health_check():
    try:
        pong = await redis_client.ping()
        return success({"redis": pong})
    except Exception as e:
        return error(str(e))

@api_router.post("/api/text_infer_async")
async def text_infer_async(content: str = Form(...), api_key: str = Depends(api_key_header)):
    task = text_inference_task.delay(content)
    return success({"task_id": task.id})

@api_router.post("/api/image_infer_async")
async def image_infer_async(file: UploadFile = File(...), api_key: str = Depends(api_key_header)):
    file_location = save_upload_file(file)
    task = image_inference_task.delay(file_location)
    return success({"task_id": task.id})

@api_router.post("/api/audio_infer_async")
async def audio_infer_async(file: UploadFile = File(...), api_key: str = Depends(api_key_header)):
    file_location = save_upload_file(file)
    task = audio_inference_task.delay(file_location)
    return success({"task_id": task.id})


# === 异步任务结果查询 ===

@api_router.get("/api/task_result/{task_id}")
async def get_task_result(task_id: str, api_key: str = Depends(api_key_header)):
    res = AsyncResult(task_id)
    result = res.result if res.ready() else None
    return success({"status": res.status, "result": result})


# === 多模态任务 ===

@api_router.post("/api/multimodal_infer_async")
async def multimodal_infer_async(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    api_key: str = Depends(api_key_header),
):
    image_path = save_upload_file(image) if image else None
    audio_path = save_upload_file(audio) if audio else None

    task_ids = await manager.dispatch_tasks(text=text, image_path=image_path, audio_path=audio_path)
    return success({"task_ids": task_ids})

@api_router.get("/api/multimodal_result")
async def multimodal_result(task_ids: str, api_key: str = Depends(api_key_header)):
    try:
        task_id_dict = json.loads(task_ids)
    except Exception:
        return error("task_ids 格式错误")
    results = await manager.aggregate_results(task_id_dict)
    return success(results)


# === 多模态 Agent 智能体任务 ===

@api_router.post("/api/multimodal_agent_infer_async")
async def multimodal_agent_infer_async(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    api_key: str = Depends(api_key_header),
):
    image_path = save_upload_file(image) if image else None
    audio_path = save_upload_file(audio) if audio else None
    task_data = {"text": text, "image_path": image_path, "audio_path": audio_path}
    task = multimodal_agent_inference_task.delay(task_data)
    return success({"task_id": task.id})

@api_router.get("/api/multimodal_agent_result/{task_id}")
async def multimodal_agent_result(task_id: str, api_key: str = Depends(api_key_header)):
    res = AsyncResult(task_id)
    result = res.result if res.ready() else None
    return success({"status": res.status, "result": result})
