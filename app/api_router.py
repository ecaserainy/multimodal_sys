from fastapi import APIRouter, UploadFile, File,Form
from app.models.audio_model import AudioModel
from app.models.text_model import TextModel
from app.models.image_model import ImageModel
from typing import Optional
from app import cache_api
api_router = APIRouter()
api_router.include_router(cache_api.router, prefix="/api")

text_model = TextModel()
image_model = ImageModel()
audio_model = AudioModel()

@api_router.post("/chat/multimodal")
async def multimodal_chat(
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    image_caption = None
    audio_transcript = None

    if image:
        image_path = f"./data/{image.filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())
        image_caption = image_model.generate_caption(image_path)

    if audio:
        audio_path = f"./data/{audio.filename}"
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
        return {"error": "请至少提供文本、图片或音频中的一项"}

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

@api_router.get("/text")
async def text_test(prompt: str = "你好，请自我介绍"):
    reply = text_model.generate(prompt)
    return {"reply": reply}

@api_router.post("/image")
async def image_test(file: UploadFile = File(...)):
    image_path = f"./data/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())
    result = image_model.generate_caption(image_path)
    return {"caption": result}

@api_router.post("/audio")
async def audio_test(file: UploadFile = File(...)):
    audio_path = f"./data/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    result = audio_model.transcribe(audio_path)
    return {"transcription": result}