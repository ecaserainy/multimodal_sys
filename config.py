import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 模型路径
    TEXT_MODEL_PATH = os.getenv("TEXT_MODEL_PATH", "Models/DeepSeek-R1-Distill-Qwen-1.5B")
    IMAGE_MODEL_PATH = os.getenv("IMAGE_MODEL_PATH", "Models/SmolVLM-Instruct")
    AUDIO_MODEL_PATH = os.getenv("AUDIO_MODEL_PATH", "Models/whisper-medium")

    # RAG 知识库配置
    RAG_DATA_DIR = os.getenv("RAG_DATA_DIR", "data/rag_doc")
    RAG_PERSIST_DIR = os.getenv("RAG_PERSIST_DIR", "storage")
    EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "Models/bge-small-zh-v1.5")

    # Redis 配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

    # Celery 配置
    USE_CELERY = os.getenv("USE_CELERY", "True").lower() == "true"
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # 安全配置
    API_KEY = os.getenv("API_KEY", "default-secret-key")
    API_KEY_NAME = "X-API-Key"

    # 上传路径
    BASE_UPLOAD_DIR = os.getenv("BASE_UPLOAD_DIR", "temp_uploads")
