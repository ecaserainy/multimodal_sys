import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 模型路径
    TEXT_MODEL_PATH = os.getenv("TEXT_MODEL_PATH", "Models/DeepSeek-R1-Distill-Qwen-1.5B")
    IMAGE_MODEL_PATH = os.getenv("IMAGE_MODEL_PATH", "Models/llava-v1.6-vicuna-7b")
    AUDIO_MODEL_PATH = os.getenv("AUDIO_MODEL_PATH", "Models/whisper-medium")

    # 知识库配置
    RAG_DATA_DIR = os.getenv("RAG_DATA_DIR", "data/rag_documents")
    RAG_PERSIST_DIR = os.getenv("RAG_PERSIST_DIR", "storage")

    # Redis配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # API安全
    API_KEY = os.getenv("API_KEY", "default-secret-key")