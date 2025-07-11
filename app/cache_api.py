from fastapi import APIRouter, Request, File, Form, Depends , HTTPException
from typing import Optional
import uuid
import aiofiles
import os
import json
from services.cache import redis_client
from services.auth_manager import verify_api_key

router = APIRouter()
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/multimodal")
async def multimodal_enqueue(
    request: Request,
    text: Optional[str] = Form(None),
    image: Optional[bytes] = File(None),
    image_filename: Optional[str] = Form(None),
    audio: Optional[bytes] = File(None),
    audio_filename: Optional[str] = Form(None),
    _: None = Depends(verify_api_key),
):
    task_id = str(uuid.uuid4())

    image_path = None
    if image:
        if not image_filename:
            image_filename = f"{task_id}_image"
        image_path = os.path.join(DATA_DIR, image_filename)
        async with aiofiles.open(image_path, 'wb') as f:
            await f.write(image)

    audio_path = None
    if audio:
        if not audio_filename:
            audio_filename = f"{task_id}_audio"
        audio_path = os.path.join(DATA_DIR, audio_filename)
        async with aiofiles.open(audio_path, 'wb') as f:
            await f.write(audio)

    task_data = {
        "task_id": task_id,
        "input": {
            "text": text,
            "image_path": image_path,
            "audio_path": audio_path
        }
    }
    task_json = json.dumps(task_data)
    await redis_client.rpush("multimodal_queue", task_json)

    return {"status": "queued", "task_id": task_id}

@router.get("/multimodal/result/{task_id}")
async def get_result(task_id: str,_: None = Depends(verify_api_key),):
    result_key = f"multimodal_result:{task_id}"
    result = await redis_client.get(result_key)
    if not result:
        return {"status": "processing", "detail": "Result not ready or invalid task_id."}
    try:
        data = json.loads(result)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse result.")
    return {"status": "done", "result": data}