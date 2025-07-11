import torch
from app.models.text_model import load_text_model
from app.models.image_model import load_image_model
from app.models.audio_model import load_audio_model


class ModelContainer:
    def __init__(self):
        self._text_model = None
        self._image_model = None
        self._audio_model = None

    @property
    def text_model(self):
        if not self._text_model:
            print("[Container] Loading text model...")
            self._text_model = load_text_model()
        return self._text_model

    @property
    def image_model(self):
        if not self._image_model:
            print("[Container] Loading image model...")
            self._image_model = load_image_model()
        return self._image_model

    @property
    def audio_model(self):
        if not self._audio_model:
            print("[Container] Loading audio model...")
            self._audio_model = load_audio_model()
        return self._audio_model

    def release_resources(self):
        """显式释放模型资源"""
        if self._text_model:
            del self._text_model
            self._text_model = None
        if self._image_model:
            del self._image_model
            self._image_model = None
        if self._audio_model:
            del self._audio_model
            self._audio_model = None
        torch.cuda.empty_cache()
        print("[Container] Models released")


# 全局容器实例
container = ModelContainer()