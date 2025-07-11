from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
import os
import json

from app.models.text_model import TextModel
from app.models.image_model import ImageModel
from app.models.audio_model import AudioModel
from services.multimodal_manager import MultimodalManager
from services.cache import redis_client

from tasks.text_task import text_inference_task
from tasks.image_task import image_inference_task
from tasks.audio_task import audio_inference_task
from tasks.multimodal_agent_task import multimodal_agent_inference_task

api_router = APIRouter()

text_model = TextModel()
image_model = ImageModel()
audio_model = AudioModel()

UPLOAD_DIR = "./data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@api_router.get("/health")
async def health_check():
    try:
        pong = await redis_client.ping()
        return {"status": "ok", "redis": pong}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@api_router.post("/chat/multimodal_sync")
async def multimodal_chat_sync(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    image_caption = None
    audio_transcript = None

    if image:
        image_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        image_caption = image_model.generate_caption(image_path)

    if audio:
        audio_path = os.path.join(UPLOAD_DIR, audio.filename)
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
        audio_transcript = audio_model.transcribe(audio_path)

    combined_prompt = ""
    if text:
        combined_prompt += f"用户输入：{text}\n"
    if image_caption:
        combined_prompt += f"图片内容：{image_caption}\n"
    if audio_transcript:
        combined_prompt += f"语音内容：{audio_transcript}\n"

    if not combined_prompt:
        return JSONResponse({"error": "请至少提供文本、图片或音频中的一项"}, status_code=400)

    reply = text_model.generate(combined_prompt)

    return {
        "input": {
            "text": text,
            "image": image.filename if image else None,
            "audio": audio.filename if audio else None
        },
        "intermediate": {
            "image_caption": image_caption,
            "audio_transcript": audio_transcript
        },
        "reply": reply
    }


def save_upload_file(file: UploadFile) -> str:
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


@api_router.post("/api/text_infer_async")
async def text_infer_async(content: str = Form(...)):
    task = text_inference_task.delay(content)
    return {"task_id": task.id}


@api_router.post("/api/image_infer_async")
async def image_infer_async(file: UploadFile = File(...)):
    file_location = save_upload_file(file)
    task = image_inference_task.delay(file_location)
    return {"task_id": task.id}


@api_router.post("/api/audio_infer_async")
async def audio_infer_async(file: UploadFile = File(...)):
    file_location = save_upload_file(file)
    task = audio_inference_task.delay(file_location)
    return {"task_id": task.id}


@api_router.get("/api/task_result/{task_id}")
async def get_task_result(task_id: str):
    res = AsyncResult(task_id)
    if res.ready():
        return {"status": res.status, "result": res.result}
    else:
        return {"status": res.status, "result": None}


@api_router.post("/api/multimodal_infer_async")
async def multimodal_infer_async(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    manager = MultimodalManager(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    image_path, audio_path = None, None
    if image:
        image_path = save_upload_file(image)
    if audio:
        audio_path = save_upload_file(audio)

    task_ids = await manager.dispatch_tasks(text=text, image_path=image_path, audio_path=audio_path)
    return {"task_ids": task_ids}


@api_router.get("/api/multimodal_result")
async def multimodal_result(task_ids: str):
    try:
        task_id_dict = json.loads(task_ids)
    except Exception:
        return JSONResponse({"error": "task_ids格式错误"}, status_code=400)

    from services.multimodal_manager import MultimodalManager
    manager = MultimodalManager()
    results = await manager.aggregate_results(task_id_dict)
    return results


@api_router.post("/api/multimodal_agent_infer_async")
async def multimodal_agent_infer_async(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    image_path, audio_path = None, None
    if image:
        image_path = save_upload_file(image)
    if audio:
        audio_path = save_upload_file(audio)

    task_data = {
        "text": text,
        "image_path": image_path,
        "audio_path": audio_path,
    }
    task = multimodal_agent_inference_task.delay(task_data)
    return {"task_id": task.id}


@api_router.get("/api/multimodal_agent_result/{task_id}")
async def multimodal_agent_result(task_id: str):
    res = AsyncResult(task_id)
    if res.ready():
        return {"status": res.status, "result": res.result}
    else:
        return {"status": res.status, "result": None}


@api_router.get("/text")
async def text_test(prompt: str = "你好，请自我介绍"):
    reply = text_model.generate(prompt)
    return {"reply": reply}


@api_router.post("/image")
async def image_test(file: UploadFile = File(...)):
    image_path = save_upload_file(file)
    result = image_model.generate_caption(image_path)
    return {"caption": result}


@api_router.post("/audio")
async def audio_test(file: UploadFile = File(...)):
    audio_path = save_upload_file(file)
    result = audio_model.transcribe(audio_path)
    return {"transcription": result}
