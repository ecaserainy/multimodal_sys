import uvicorn, asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api_router import api_router
from services.queue_manager import worker
from app.api_router import text_model, image_model, audio_model
import torch

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] FastAPI starting...")

    task = asyncio.create_task(worker())
    yield
    print("[Shutdown] Releasing models and GPU memory...")

    if text_model.model:
        del text_model.model
        del text_model.tokenizer

    if image_model.model:
        del image_model.model
        del image_model.processor

    if audio_model.pipe:
        del audio_model.pipe
    torch.cuda.empty_cache()
    task.cancel()
    print("[Shutdown] All resources released.")

app = FastAPI(title="Multimodal Customer Service", lifespan=lifespan)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
