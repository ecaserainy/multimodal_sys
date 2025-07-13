import os
import time
from dotenv import load_dotenv
from contextlib import asynccontextmanager

import uvicorn
from celery.result import AsyncResult
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api_router import api_router
from utils.file_utils import BASE_UPLOAD_DIR
from config import Config
from utils.exception_handler import http_exception_handler, validation_exception_handler
from services.di import get_container
from tasks.audio_task import audio_inference_task
from tasks.image_task import image_inference_task
from tasks.text_task import text_inference_task

load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = get_container()
    app.state.container = container

    print("[Startup] FastAPI starting...")
    yield

    print("[Shutdown] Releasing resources...")
    container.release_resources()
    print("[Shutdown] All resources released.")

app = FastAPI(title="Multimodal Customer Service", lifespan=lifespan)

app.include_router(api_router)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.post("/api/multimodal_infer_async")
async def multimodal_infer_async(
    text: str = Form(None),
    image: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    os.makedirs("temp_uploads", exist_ok=True)

    image_path, audio_path = None, None
    if image:
        image_path = f"temp_uploads/{image.filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())
    if audio:
        audio_path = f"temp_uploads/{audio.filename}"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

    task_ids = await get_container().multimodal_manager.dispatch_tasks(
        text=text, image_path=image_path, audio_path=audio_path)
    return JSONResponse({"task_ids": task_ids})

@app.get("/api/multimodal_result")
async def multimodal_result(task_ids: str):
    import json
    try:
        task_id_dict = json.loads(task_ids)
    except Exception:
        return JSONResponse({"error": "task_ids格式错误"}, status_code=400)

    results = await get_container().multimodal_manager.aggregate_results(task_id_dict)
    return results

@app.get("/health")
async def health_check():
    return {"status": "ok"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Multimodal Customer Service",
        version="1.0.0",
        description="API for multimodal processing (text, image, audio) with Celery async tasks",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": API_KEY_NAME,
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"ApiKeyAuth": []}])
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

@app.post("/api/text_infer_async")
async def text_infer_async(content: str = Form(...)):
    task = text_inference_task.delay(content)
    return {"task_id": task.id}

@app.post("/api/image_infer_async")
async def image_infer_async(file: UploadFile = File(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    file_location = f"temp_uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    task = image_inference_task.delay(file_location)
    return {"task_id": task.id}

@app.post("/api/audio_infer_async")
async def audio_infer_async(file: UploadFile = File(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    file_location = f"temp_uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    task = audio_inference_task.delay(file_location)
    return {"task_id": task.id}

@app.get("/api/task_result/{task_id}")
async def get_task_result(task_id: str):
    res = AsyncResult(task_id)
    if res.ready():
        return {"status": res.status, "result": res.result}
    else:
        return {"status": res.status, "result": None}

def clear_upload_dir(expire_seconds=3600):
    now = time.time()
    for file in BASE_UPLOAD_DIR.iterdir():
        if file.is_file():
            file_age = now - file.stat().st_mtime
            if file_age > expire_seconds:
                try:
                    file.unlink()
                except Exception:
                    pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    print("FastAPI server started")
