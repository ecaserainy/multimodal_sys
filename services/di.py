from app.models.text_model import TextModel
from app.models.image_model import ImageModel
from app.models.audio_model import AudioModel


class Container:
    def __init__(self):
        self._text_model = None
        self._image_model = None
        self._audio_model = None

    @property
    def text_model(self):
        if self._text_model is None:
            self._text_model = TextModel()
        return self._text_model

    @property
    def image_model(self):
        if self._image_model is None:
            self._image_model = ImageModel()
        return self._image_model

    @property
    def audio_model(self):
        if self._audio_model is None:
            self._audio_model = AudioModel()
        return self._audio_model

    def release_resources(self):
        self._text_model = None
        self._image_model = None
        self._audio_model = None


_container = None

def get_container():
    global _container
    if _container is None:
        _container = Container()
    return _container
